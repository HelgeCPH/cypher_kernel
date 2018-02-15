import os
import yaml
import shutil
from jinja2 import Template
from ipykernel.kernelbase import Kernel
from pexpect.replwrap import REPLWrapper
from .cypher_utils import Node, Relation, parse_output


class CypherKernel(Kernel):
    implementation = 'Cypher'
    implementation_version = '0.1'
    language = 'cypher'
    language_version = '0.1'
    language_info = {
        'name': 'Any text',
        'mimetype': 'text/cypher',
        'file_extension': '.cql',
    }
    banner = "Cypher kernel - Neo4j in Jupyter Notebooks"

    # Got the keywords from:
    # http://neo4j.com/docs/developer-manual/current/cypher/syntax/reserved/
    keywords = ['CALL', 'CREATE', 'DELETE', 'DETACH', 'EXISTS', 'FOREACH', 
                'LOAD', 'MATCH', 'MERGE', 'OPTIONAL', 'REMOVE', 'RETURN', 
                'SET', 'START', 'UNION', 'UNWIND', 'WITH', 'LIMIT', 'ORDER', 
                'SKIP', 'WHERE', 'YIELD', 'ASC', 'ASCENDING', 'ASSERT', 'BY', 
                'CSV', 'DESC', 'DESCENDING', 'ON', 'ALL', 'CASE', 'ELSE', 
                'END', 'THEN', 'WHEN', 'AND', 'AS', 'CONTAINS', 'DISTINCT', 
                'ENDS', 'IN', 'IS', 'NOT', 'OR', 'STARTS', 'XOR', 'CONSTRAINT',
                'CREATE', 'DROP', 'EXISTS', 'INDEX', 'NODE', 'KEY', 'UNIQUE', 
                'INDEX', 'JOIN', 'PERIODIC', 'COMMIT', 'SCAN', 'USING', 
                'false', 'null', 'true', 'ADD', 'DO', 'FOR', 'MANDATORY', 'OF',
                'REQUIRE', 'SCALAR']
 
    @property
    def cfg(self):
        cfg = CypherKernel._parse_config()
        return cfg

    @property
    def user(self):
        return self.cfg['user']

    @property
    def pwd(self):
        return self.cfg['pwd']

    @property
    def host(self):
        return self.cfg['host']

    @property
    def connect_result_nodes(self):
        return self.cfg['connect_result_nodes']

    @property
    def cypher_shell(self):
        # cypher_shell_bin = shutil.which('cypher-shell')
        # TODO: figure out how to make this binary part of the package/release
        cypher_shell_bin = '/Users/rhp/Documents/workspace/Java/cypher-shell/cypher-shell/build/install/cypher-shell/cypher-shell'
        cypher = REPLWrapper(f'{cypher_shell_bin} -u {self.user} -p {self.pwd} --format verbose', 'neo4j> ', None)
        return cypher

    @staticmethod
    def _parse_config():
        """
        Parses spawn YAML command options from the default Jupyter configuration directory.
        http://jupyter.readthedocs.io/en/latest/projects/jupyter-directories.html#configuration-files
        """
        config_dir = os.environ.get('JUPYTER_CONFIG_DIR')
        if not config_dir:
            config_dir = '.jupyter'
        config_path = os.path.join(os.path.expanduser(
            '~'), config_dir, 'cypher_config.yml')
        default_config = {'user': 'neo4j', 
                          'pwd': 'neo4j', 
                          'host': 'localhost:7474',
                          'connect_result_nodes': False}
        try:
            config = yaml.load(open(config_path))
            if len([k for k in ['user', 'pwd', 'host', 'connect_result_nodes'] 
                        if k in config.keys()]) == 4:
                return config
        except FileNotFoundError:
            # Using default configuration
            return default_config
        return default_config

    def _response_to_html(self, nodes, relations, node_types=[]):

        template_str =  '''<html>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/alchemyjs/0.4.2/alchemy.min.css" />
  <div class="alchemy" id="alchemy"></div>
  <script src="https://d3js.org/d3.v3.min.js" charset="utf-8"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/alchemyjs/0.4.2/alchemy.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/alchemyjs/0.4.2/scripts/vendor.js"></script>
  <script type="text/javascript">
    var json = {
    "nodes": [{% for n in nodes %}
              { "id": "{{ n.id }}",
                 "type": "{{ n.label }}", 
                 "caption": "{{ n.properties }}" },
              {% endfor %}],
    "edges": [{% for r in rels %}
              { "source": "{{ r.start_node }}",
                 "target": "{{ r.end_node }}", 
                 "caption": "{{ r.properties }}" },
              {% endfor %}],
};
    var config = {
      dataSource: json,
      forceLocked: false,
      graphHeight: function(){ return 400; },
      // graphWidth: function(){ return 400; },      
      linkDistance: function(){ return 40; },
    };
    
    alchemy = new Alchemy(config);
  </script>
'''
        template = Template(template_str)
        graphHTML = template.render(nodes=nodes, rels=relations)


        graphHTML = '''<html><head>
  <title>Network | Basic usage</title>

  <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/vis/4.21.0/vis.min.js"></script>
  <link href="https://cdnjs.cloudflare.com/ajax/libs/vis/4.21.0/vis.min.css" rel="stylesheet" type="text/css">

  <style type="text/css">
    #mynetwork {
      width: 600px;
      height: 400px;
      border: 1px solid lightgray;
    }
  </style>
<style></style></head>
<body>

<p>
  The types of endpoints are: <code>'arrow' 'circle' 'bar'</code>.
  The default is <code>'arrow'</code>.
</p>

<div id="mynetwork"><div class="vis-network" tabindex="900" style="position: relative; overflow: hidden; -webkit-user-select: none; -webkit-user-drag: none; width: 100%; height: 100%;"><canvas width="1200" height="800" style="position: relative; -webkit-user-select: none; -webkit-user-drag: none; width: 100%; height: 100%;"></canvas></div></div>

<script type="text/javascript">
  // create an array with nodes
  var nodes = new vis.DataSet([
    {id: 1, label: 'A'},
    {id: 2, label: 'B'},
    {id: 3, label: 'C'},
    {id: 4, label: 'D'}
  ]);

  // create an array with edges
  var edges = new vis.DataSet([
    {from: 1, to: 2, arrows:'to', title:'OIOIOI<br>AIAIAI'},
    {from: 2, to: 3, arrows:'to', title:'OIOIOI<br>AIAIAI'},
    {from: 3, to: 4, arrows:'to', title:'OIOIOI<br>AIAIAI'},
  ]);

  // create a network
  var container = document.getElementById('mynetwork');
  var data = {
    nodes: nodes,
    edges: edges
  };

  var options = {
/*
    // Enable this to make the endpoints smaller/larger
    edges: {
      arrows: {
        to: {
          scaleFactor: 5
        }
      }
    }
*/
  };

  var network = new vis.Network(container, data, options);
</script>




</body></html>
'''


        return graphHTML


    def _send_query_to_cypher_shell(self, code):

        # Prepare input, remove newline characters as cypher-shell does not 
        # seem to be able to handle it...
        code = ' '.join(code.splitlines())
        if not code.endswith(';'):
            # It cannot handle strings without semicolon either
            code += ';'

        res = self.cypher_shell.run_command(code).splitlines()
        # res[0] = res[0].replace('\x1b[m', '')
        return res, '\n'.join(res[2:-1])

    def do_execute(self, code, silent, store_history=True, 
                   user_expressions=None, allow_stdin=False):
        
        line_response, text_response = self._send_query_to_cypher_shell(code)

        error, parse_result = parse_output(line_response)
        if error:
            pass
        else:
            nodes, relations = parse_result
            graphHTML = """<link href="https://cdnjs.cloudflare.com/ajax/libs/vis/4.21.0/vis.min.css" rel="stylesheet" type="text/css">

  <style type="text/css">
    #mynetwork {
      width: 600px;
      height: 400px;
      border: 1px solid lightgray;
    }
  </style>
<div id="mynetwork"><div class="vis-network" tabindex="900" style="position: relative; overflow: hidden; -webkit-user-select: none; -webkit-user-drag: none; width: 100%; height: 100%;"><canvas width="1200" height="800" style="position: relative; -webkit-user-select: none; -webkit-user-drag: none; width: 100%; height: 100%;"></canvas></div></div>"""
            
            # graphHTML = """<style></style><div id="test"></div>"""

             # self._response_to_html(nodes, relations)

            if not silent:
                html_msg = {'data': {'text/html': graphHTML}, 'execution_count' : self.execution_count}
                # js_str = 'require(["https://d3js.org/d3.v3.min.js"]);' 
                
                js_str = '''require(["https://cdnjs.cloudflare.com/ajax/libs/vis/4.21.0/vis.min.js"], function() {
console.log("Hello!")
  var nodes = new vis.DataSet([
    {id: 1, label: 'A'},
    {id: 2, label: 'B'},
    {id: 3, label: 'C'},
    {id: 4, label: 'D'}
  ]);

  // create an array with edges
  var edges = new vis.DataSet([
    {from: 1, to: 2, arrows:'to', title:'OIOIOI<br>AIAIAI'},
    {from: 2, to: 3, arrows:'to', title:'OIOIOI<br>AIAIAI'},
    {from: 3, to: 4, arrows:'to', title:'OIOIOI<br>AIAIAI'},
  ]);

  // create a network
  var container = document.getElementById('mynetwork');
  var data = {
    nodes: nodes,
    edges: edges
  };

  var options = {
/*
    // Enable this to make the endpoints smaller/larger
    edges: {
      arrows: {
        to: {
          scaleFactor: 5
        }
      }
    }
*/
  };

  var network = new vis.Network(container, data, options);});'''


  
#                 js_str = '''require(["https://rawgit.com/caldwell/renderjson/master/renderjson.js"], function() {  // create an array with nodes
# document.getElementById("test").appendChild(
#     renderjson({ hello: [1,2,3,4], there: { a:1, b:2, c:["hello", null] }}))});'''

                js_msg = {'data': {'application/javascript': js_str}}
                self.send_response(self.iopub_socket, 'display_data', js_msg)
                self.send_response(self.iopub_socket, 'display_data', html_msg)

        if not silent:
            # No matter what, this is the text response
            result = {'data': {'text/plain': text_response}, 
                      'execution_count' : self.execution_count}
            self.send_response(self.iopub_socket, 'execute_result', 
                               result)


        exec_result = {'status': 'ok', 
                       'execution_count': self.execution_count,
                       'payload': [], 'user_expressions': {}}

        return exec_result

    def do_complete(self, code, cursor_pos):
        space_idxs = [i for i, l in enumerate(code) if l == ' ']
        low_idxs = [s for s in space_idxs if s < cursor_pos]
        if low_idxs:
            low_cp = max([s for s in space_idxs if s < cursor_pos]) + 1
            key_start = code[low_cp:cursor_pos]
        else:
            low_cp = 0
            key_start = code[:cursor_pos]

        matches = [k for k in self.keywords if k.startswith(key_start)]
        content = {'matches' : matches, 'cursor_start' : low_cp, 
                   'cursor_end' : cursor_pos, 'metadata' : {}, 'status' : 'ok'}
        return content