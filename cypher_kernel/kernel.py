import os
import yaml
import uuid
import shutil
import random
import platform
from jinja2 import Template
from neo4j.data import Node
from neo4j.exceptions import Neo4jError
from ipykernel.kernelbase import Kernel
from .cypher_keywords import KEYWORDS
from .neo4j_connection import Neo4jConnection
from pexpect.replwrap import REPLWrapper, bash, python


class CypherKernel(Kernel):
    implementation = "Cypher"
    implementation_version = "0.1"  # cypher_kernel.__version__
    language = "cypher"
    language_version = "0.1"
    language_info = {
        # Switched that to cypher, see
        # https://github.com/jupyter/help/issues/301
        "name": "cypher",
        "mimetype": "text/cypher",
        "file_extension": ".cql",
    }
    banner = "Cypher kernel - Neo4j in Jupyter Notebooks"
    keywords = KEYWORDS

    global_node_colors = {}

    my_python = python(command="python")
    my_python.run_command(
        """import ast
import pandas as pd
import networkx as nx
G = nx.Graph()
df = pd.DataFrame()"""
    )

    if platform.system() == "Windows":
        # TODO: what shall I do on Windows here???
        # my_shell = ...
        pass
    else:
        my_shell = bash(command="bash")

    @property
    def cfg(self):
        cfg = CypherKernel._parse_config()
        return cfg

    @property
    def user(self):
        return self.cfg["user"]

    @property
    def pwd(self):
        return self.cfg["pwd"]

    @property
    def host(self):
        return self.cfg["host"]

    @property
    def connect_result_nodes(self):
        return self.cfg["connect_result_nodes"]

    def __init__(self, **kwargs):
        Kernel.__init__(self, **kwargs)
        # establish connection to DB
        self.conn = Neo4jConnection()

    @staticmethod
    def _parse_config():
        """
        Parses spawn YAML command options from the default Jupyter configuration directory.
        http://jupyter.readthedocs.io/en/latest/projects/jupyter-directories.html#configuration-files
        """
        config_dir = os.environ.get("JUPYTER_CONFIG_DIR")
        if not config_dir:
            config_dir = ".jupyter"
        config_path = os.path.join(os.path.expanduser("~"), config_dir, "cypher_config.yml")
        default_config = {
            "user": "neo4j",
            "pwd": "neo4j",
            "host": "neo4j://localhost:7687",
            "connect_result_nodes": False,
        }
        try:
            config = yaml.load(open(config_path), Loader=yaml.FullLoader)
            if len([k for k in ["user", "pwd", "host", "connect_result_nodes"] if k in config.keys()]) == 5:
                return config
        except FileNotFoundError:
            # Using default configuration
            return default_config
        return default_config

    def _response_to_js_graph(self, nodes, relations, element_id):
        template_str = """require(["https://cdnjs.cloudflare.com/ajax/libs/vis/4.21.0/vis.min.js"], function(vis) {
  var nodes = new vis.DataSet([
    {% for n in nodes %}{ id: {{ n.id }}, label: "{{ label_picker(n.labels) }}", title: "{{ n._properties }}", color: 'rgba({{ node_colors[label_picker(n.labels)] }})'},
    {% endfor %}
  ]);

  // create an array with edges
  var edges = new vis.DataSet([
    {% for r in rels %}{ from: {{ r.nodes[0].id }},to: {{ r.nodes[1].id }}, arrows:'to', title: "{{ r.type }}" },
    {% endfor %}
  ]);

  // create a network
  var container = document.getElementById('{{element_id}}');
  var data = {
    nodes: nodes,
    edges: edges
  };

  var options = {
    edges: {
      arrows: {
        to: {
          scaleFactor: 0.5
        }
      }
    },
    width: '100%',
    height: '500px',
    interaction: {hover: true}
  };

  var network = new vis.Network(container, data, options);});
"""

        def label_picker(frozenset):
            """This function is only necessary, since frozensets cannot be easily cast to lists in Jinja2"""
            return list(frozenset)[0]

        template = Template(template_str)
        graphJS = template.render(
            nodes=nodes,
            rels=relations,
            element_id=element_id,
            node_colors=self.global_node_colors,
            label_picker=label_picker,
        )

        return graphJS

    def _color_nodes(self, nodes):
        for n in nodes:
            labels_lst = list(n.labels)
            if not labels_lst[0] in self.global_node_colors.keys():
                rgb = [str(random.randint(0, 255)) for _ in range(3)]
                rgba = rgb + ["0.5"]
                self.global_node_colors[labels_lst[0]] = ",".join(rgba)

    def _clean_input(self, code):
        lines = code.splitlines()
        clean_input = "\n".join([l for l in lines if l])
        return clean_input

    def _is_magic(self, code):
        magic_lines = code.splitlines()
        magic_line = magic_lines[0].strip()
        if magic_line.startswith("%%"):
            return magic_line.replace("%%", ""), "\n".join(magic_lines[1:])
        else:
            return None, None

    def _send_to_bash(self, code):
        res = self.my_shell.run_command(code, timeout=self.cmd_timeout)
        return res

    def _send_to_python(self, code):
        res = self.my_python.run_command(code, timeout=self.cmd_timeout)
        return res

    def _push_to_python_env(self, header, content):
        code = '''header = ast.literal_eval("""{}""")
content = ast.literal_eval("""{}""")
df = pd.DataFrame(content, columns=header)
df'''.format(
            str(header).replace("'", "\\'"), str(content).replace("'", "\\'")
        )
        res = self._send_to_python(code)
        return res

    def do_execute(self, code, silent, store_history=True, user_expressions=None, allow_stdin=False):

        clean_input = self._clean_input(code)
        magic, magic_code = self._is_magic(code)
        # if magic == "bash" and magic_code:
        #     response = self._send_to_bash(magic_code)
        #     if not silent:
        #         result = {"data": {"text/plain": response}, "execution_count": self.execution_count}
        #         self.send_response(self.iopub_socket, "execute_result", result)

        #     exec_result = {
        #         "status": "ok",
        #         "execution_count": self.execution_count,
        #         "payload": [],
        #         "user_expressions": {},
        #     }

        #     return exec_result
        # elif magic == "python":
        #     # TODO! implement me, convert latest cypher query to networkx graph
        #     response = self._send_to_python(magic_code)
        #     if not silent:
        #         result = {"data": {"text/plain": response}, "execution_count": self.execution_count}
        #         self.send_response(self.iopub_socket, "execute_result", result)

        #     exec_result = {
        #         "status": "ok",
        #         "execution_count": self.execution_count,
        #         "payload": [],
        #         "user_expressions": {},
        #     }
        #     return exec_result
        # elif magic:
        #     # TODO: implement an error for any other magic
        #     exec_result = {
        #         "status": "error",
        #         "execution_count": self.execution_count,
        #         "payload": [],
        #         "user_expressions": {},
        #     }
        #     return exec_result

        # then it is a query to Cypher
        try:
            response = self.conn.query(code)
        except Neo4jError as e:
            # TODO: send results as proper errors here
            exec_result = {
                "status": "error",
                "execution_count": self.execution_count,
                "payload": [e.message],
                "user_expressions": {},
            }
            return exec_result

        # Split nodes and relations from response records for later visualization
        nodes, relations = set([]), set([])
        for record in response:
            for el in record:
                if type(el) == Node:
                    nodes.add(el)
                else:
                    # Then it is a relation wrapped into an abstract base class
                    relations.add(el)

        # df_header, df_content = parse_output_to_python(text_response)
        # if df_header and df_content:
        #     _ = self._push_to_python_env(df_header, df_content)

        self._color_nodes(nodes)

        if not silent and nodes:
            # Only return the visual output when there are actually nodes and relations, as long as auto connection is not implemented also put it there when only nodes exist
            element_id = uuid.uuid4()
            graphJS = self._response_to_js_graph(nodes, relations, element_id)

            graph_HTML_tmpl = """<link href="https://cdnjs.cloudflare.com/ajax/libs/vis/4.21.0/vis.min.css" rel="stylesheet" type="text/css">
            <div id="{{ element_id }}"></div>
            """
            html_template = Template(graph_HTML_tmpl)
            graph_HTML = html_template.render(element_id=element_id)

            html_msg = {"data": {"text/html": graph_HTML}, "execution_count": self.execution_count}
            js_msg = {"data": {"application/javascript": graphJS}}
            self.send_response(self.iopub_socket, "display_data", js_msg)
            self.send_response(self.iopub_socket, "display_data", html_msg)

        if not silent:
            # No matter what, this is the text response
            text_response = str(response)
            result = {"data": {"text/plain": text_response}, "execution_count": self.execution_count}
            self.send_response(self.iopub_socket, "execute_result", result)

        exec_result = {"status": "ok", "execution_count": self.execution_count, "payload": [], "user_expressions": {}}

        return exec_result

    def do_complete(self, code, cursor_pos):
        space_idxs = [i for i, l in enumerate(code) if l == " "]
        low_idxs = [s for s in space_idxs if s < cursor_pos]
        if low_idxs:
            low_cp = max([s for s in space_idxs if s < cursor_pos]) + 1
            key_start = code[low_cp:cursor_pos]
        else:
            low_cp = 0
            key_start = code[:cursor_pos]

        matches = [k for k in self.keywords if k.startswith(key_start)]
        content = {"matches": matches, "cursor_start": low_cp, "cursor_end": cursor_pos, "metadata": {}, "status": "ok"}
        return content
