import os
import sys
import json
import yaml
import uuid
import random
import platform
from jinja2 import Template
from neo4j.data import Node, Relationship
from neo4j.exceptions import Neo4jError
from ipykernel.kernelbase import Kernel
from .cypher_keywords import KEYWORDS
from .neo4j_connection import Neo4jConnection
from pexpect.replwrap import bash, python


class CypherKernel(Kernel):
    implementation = "Cypher"
    implementation_version = sys.modules[__package__].__version__
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

    @property
    def cmd_timeout(self):
        return self.cfg["cmd_timeout"]

    def __init__(self, **kwargs):
        Kernel.__init__(self, **kwargs)
        # establish connection to DB
        self.conn = Neo4jConnection(uri=self.host, user=self.user, pwd=self.pwd)

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
            "pwd": "pwd",
            "host": "neo4j://localhost:7687",
            "connect_result_nodes": False,
            "cmd_timeout": None,
        }
        try:
            config = yaml.load(open(config_path), Loader=yaml.FullLoader)
            if len([k for k in default_config.keys() if k in config.keys()]) == 5:
                return config
        except FileNotFoundError:
            # Using default configuration
            return default_config
        return default_config

    def _response_to_js_graph(self, nodes, relations, element_id):
        template_str = """require(["https://cdnjs.cloudflare.com/ajax/libs/vis/4.21.0/vis.min.js"], function(vis) {
  var nodes = new vis.DataSet([
    {% for n in nodes %}{ id: {{ n.id }}, label: "{{ label_picker(n.labels) }}", title: "{{ properties_serializer(n._properties) }}", color: 'rgba({{ node_colors[label_picker(n.labels)] }})'},
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

        def escape_strs(properties_dict):
            properties_str = "{"
            for k, v in properties_dict.items():
                if type(v) == str and "'" in v:
                    v.replace("'", "'")
                    # v.replace('"', '\"')
                properties_str += k + ":" + str(v) + ",<br>"
            properties_str = properties_str[:-5] + "}"
            return properties_str

        template = Template(template_str)
        graph_js = template.render(
            nodes=nodes,
            rels=relations,
            element_id=element_id,
            node_colors=self.global_node_colors,
            label_picker=label_picker,
            properties_serializer=escape_strs,
        )

        with open("/tmp/out.js", "w") as fp:
            fp.write(graph_js)
        return graph_js

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

    def _construct_and_send_text_response(self, response, is_silent, status="ok"):
        if not is_silent:
            result = {"data": {"text/plain": response}, "execution_count": self.execution_count}
            self.send_response(self.iopub_socket, "execute_result", result)

        exec_result = {
            "status": status,
            "execution_count": self.execution_count,
            "payload": [],
            "user_expressions": {},
        }
        return exec_result

    def _construct_and_send_html_response(self, nodes, relations, is_silent, status="ok"):
        element_id = uuid.uuid4()
        graph_js = self._response_to_js_graph(nodes, relations, element_id)

        graph_HTML_tmpl = """<link href="https://cdnjs.cloudflare.com/ajax/libs/vis/4.21.0/vis.min.css" rel="stylesheet" type="text/css">
        <div id="{{ element_id }}"></div>
        """
        html_template = Template(graph_HTML_tmpl)
        graph_HTML = html_template.render(element_id=element_id)

        html_msg = {"data": {"text/html": graph_HTML}, "execution_count": self.execution_count}
        js_msg = {"data": {"application/javascript": graph_js}}
        self.send_response(self.iopub_socket, "display_data", js_msg)
        self.send_response(self.iopub_socket, "display_data", html_msg)

        exec_result = {"status": status, "execution_count": self.execution_count, "payload": [], "user_expressions": {}}
        return exec_result

    def _process_response(self, response):
        """Split nodes and relations from response records for later visualization"""
        nodes, relations = set([]), set([])
        text_response = ""
        for record in response:
            for el in record:
                if isinstance(el, Node):
                    nodes.add(el)
                elif isinstance(el, Relationship):
                    # Then it is a relation wrapped into an abstract base class
                    relations.add(el)
                else:
                    text_response += str(el) + "\n"
        return nodes, relations, text_response

    def do_execute(self, code, silent, store_history=True, user_expressions=None, allow_stdin=False):

        clean_input = self._clean_input(code)
        magic, magic_code = self._is_magic(code)
        if magic == "bash" and magic_code:
            response = self._send_to_bash(magic_code)
            exec_result = self._construct_and_send_text_response(response, silent)
            return exec_result
        elif magic == "python":
            # TODO! implement me, convert latest cypher query to networkx graph
            response = self._send_to_python(magic_code)
            exec_result = self._construct_and_send_text_response(response, silent)
            return exec_result
        elif magic == None:
            # then it is a query to Cypher
            try:
                # Run the actual cypher query
                response = self.conn.query(code)
            except Neo4jError as e:
                # Send an error message to the text output
                exec_result = self._construct_and_send_text_response(e.message, silent, status="error")
                return exec_result

            nodes, relations, text_response = self._process_response(response)

            # TODO: push results to python env via to_df() method on results
            # df_header, df_content = parse_output_to_python(text_response)
            # if df_header and df_content:
            #     _ = self._push_to_python_env(df_header, df_content)

            if not silent and nodes:
                # Only return the visual output when there are actually nodes and relations,
                # as long as auto connection is not implemented also put it there when only nodes exist
                self._color_nodes(nodes)
                exec_result = self._construct_and_send_html_response(nodes, relations, silent, status="ok")
                return exec_result
            if not silent:
                # No matter what, this is the text response
                exec_result = self._construct_and_send_text_response(text_response, silent)
                return exec_result
        else:
            response = f"Unknown magic type: {magic}"
            exec_result = self._construct_and_send_text_response(response, silent, status="error")
            return exec_result
        # TODO: What should the exec_result be in case of silence?
        return None

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
