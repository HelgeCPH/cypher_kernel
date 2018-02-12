import os
import json
import yaml
import requests
from jinja2 import Template
from base64 import b64encode
from ipykernel.kernelbase import Kernel


class Node:
    def __init__(self, node_dict):
        self.id = int(node_dict['id'])
        self._labels = node_dict['labels']
        self.label = self._labels[0]
        self.properties = str(node_dict['properties'])
        self.properties_dict = node_dict['properties']

    def __str__(self):
        self.properties_dict['<_id>'] = self.id
        return f'(:{self.label} {self.properties_dict})'

    def __hash__(self):
        return hash(self.__str__())

    def __eq__(self, other):
        if isinstance(other, Node):
            return self.id == other.id
        else:
            return False
    
    def __ne__(self, other):
        return not self.__eq__(other)


class Relation:
    def __init__(self, rel_dict):
        self.id = int(rel_dict['id'])
        self.type = rel_dict['type']
        self.properties = str(rel_dict['properties'])
        self.start_node = rel_dict['startNode']
        self.end_node = rel_dict['endNode']
        self.properties_dict = rel_dict['properties']
    
    def __str__(self):
        self.properties_dict['<_id>'] = self.id
        return f'[:{self.type} {self.properties_dict}]'

    def __hash__(self):
        return hash(self.__str__())

    def __eq__(self, other):
        if isinstance(other, Relation):
            return self.id == other.id
        else:
            return False
    
    def __ne__(self, other):
        return not self.__eq__(other)


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

    keywords = ['CALL', 'CREATE', 'DELETE', 'DETACH', 'EXISTS', 'FOREACH', 'LOAD', 'MATCH', 'MERGE', 'OPTIONAL', 'REMOVE', 'RETURN', 'SET', 'START', 'UNION', 'UNWIND', 'WITH', 'LIMIT', 'ORDER', 'SKIP', 'WHERE', 'YIELD', 'ASC', 'ASCENDING', 'ASSERT', 'BY', 'CSV', 'DESC', 'DESCENDING', 'ON', 'ALL', 'CASE', 'ELSE', 'END', 'THEN', 'WHEN', 'AND', 'AS', 'CONTAINS', 'DISTINCT', 'ENDS', 'IN', 'IS', 'NOT', 'OR', 'STARTS', 'XOR', 'CONSTRAINT', 'CREATE', 'DROP', 'EXISTS', 'INDEX', 'NODE', 'KEY', 'UNIQUE', 'INDEX', 'JOIN', 'PERIODIC', 'COMMIT', 'SCAN', 'USING', 'false', 'null', 'true', 'ADD', 'DO', 'FOR', 'MANDATORY', 'OF', 'REQUIRE', 'SCALAR']

    # TODO: replace the following by a call to self._parse_config()
    cfg = {'user': 'neo4j', 
           'pwd': 'class', 
           'host': 'localhost:7474',
           'connect_result_nodes': True}
    user, pwd, host = cfg['user'], cfg['pwd'], cfg['host']
    connect_result_nodes = cfg['connect_result_nodes']
    base64_auth_str = b64encode(f'{user}:{pwd}'.encode()).decode('utf-8')
    url = f'http://{host}/db/data/transaction/commit'
    headers = {'Authorization': f'Basic {base64_auth_str}',
               'Accept': 'application/json; charset=UTF-8',
               'Content-Type': 'application/json'}

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


    def _send_query_to_neo4j(self, cypher_query):
        cypher_query
        payload = {'statements': [ 
                    {'statement': cypher_query, 
                     'resultDataContents': ['row', 'graph']
                    }]
                  }
        response = requests.post(self.url, json=payload, headers=self.headers)

        return response

    def _response_to_text(self, query_response):
        # TODO: make the text output correspond to the values in the 
        # query_response['results'][0]['columns'] fields
        columns = query_response['results'][0]['columns']
        data = query_response['results'][0]['data']

        query_result_str = ''
        query_result_nodes = []
        query_result_relations = []

        for r in data:
            nodes = r['graph']['nodes']
            relations = r['graph']['relationships']
            # I do not think I need this from the response...
            # row = r['row']
            query_result_str += f'{nodes}\n'
            query_result_str += f'{relations}\n'

            node_objs = [Node(n) for n in nodes]
            rel_objs = [Relation(n) for n in relations]

            query_result_nodes += node_objs
            query_result_relations += rel_objs

        query_result_nodes_str = str([str(n) for n in query_result_nodes])
        query_result_relations_str = str([str(r) for r in query_result_relations])
        return query_result_nodes_str + query_result_relations_str

    def _response_to_html(self, query_response):

        template_str =  '''<html>
<head>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/alchemyjs/0.4.2/alchemy.min.css" />
</head>
<body>
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
      graphWidth: function(){ return 400; },      
      linkDistance: function(){ return 40; },
    };
    
    alchemy = new Alchemy(config);
  </script>
</body>

</html>
'''
        template = Template(template_str)
        columns = query_response['results'][0]['columns']
        data = query_response['results'][0]['data']

        query_result_str = ''
        query_result_nodes = []
        query_result_relations = []

        for r in data:
            nodes = r['graph']['nodes']
            relations = r['graph']['relationships']
            # I do not think I need this from the response...
            # row = r['row']
            query_result_str += f'{nodes}\n'
            query_result_str += f'{relations}\n'

            node_objs = [Node(n) for n in nodes]
            rel_objs = [Relation(n) for n in relations]

            query_result_nodes += node_objs
            query_result_relations += rel_objs

        query_result_nodes = set(query_result_nodes)
        query_result_relations = set(query_result_relations)

        graphHTML = template.render(nodes=query_result_nodes, 
                                    rels=query_result_relations)
        return graphHTML

    def do_execute(self, code, silent, store_history=True, 
                   user_expressions=None, allow_stdin=False):
        
        response = self._send_query_to_neo4j(code)

        if response.status_code == requests.codes.ok:
            query_response = json.loads(response.text)

            if query_response['results']:
                if len(query_response['results'][0]['data']) == 1 and not query_response['results'][0]['data'][0]['graph']['nodes'] and not query_response['results'][0]['data'][0]['graph']['relationships']:
                    # This is the case for queries, which do not return any graph data
                    query_res_text = str(query_response['results'][0]['columns'][0]) + '\n' + str(query_response['results'][0]['data'][0]['row'][0])
                    if not silent:
                        result = {'data': {'text/plain': query_res_text}, 'execution_count': self.execution_count}
                        self.send_response(self.iopub_socket, 'execute_result', result)
                else:
                    graphHTML = self._response_to_html(query_response)
                    # TODO: Avoid parsing a second time the JSON response
                    query_res_text = self._response_to_text(query_response)

                    if not silent:
                        html_msg = {'data': {'text/html': graphHTML}}
                        js_str = 'require(["https://d3js.org/d3.v3.min.js"]);' 
                        #require(["https://cdnjs.cloudflare.com/ajax/libs/alchemyjs/0.4.2/alchemy.min.js"]);require(["https://cdnjs.cloudflare.com/ajax/libs/alchemyjs/0.4.2/scripts/vendor.js"]);'
                        js_msg = {'data': {'application/javascript': js_str}}
                        self.send_response(self.iopub_socket, 'display_data', js_msg)
                        self.send_response(self.iopub_socket, 'display_data', html_msg)

                        result = {'data': {'text/plain': query_res_text}, 'execution_count': self.execution_count}
                        self.send_response(self.iopub_socket, 'execute_result', result)

                        # stream_content = {'name': 'stdout', 'text': graphHTML}
                        # self.send_response(self.iopub_socket, 'stream', stream_content)
            else:
                error_msg = str(query_response['errors'][0])
                if not silent:
                    result = {'data': {'text/plain': error_msg}, 
                              'execution_count': self.execution_count}
                    self.send_response(self.iopub_socket, 'execute_result', 
                                       result)

            exec_result = {'status': 'ok', 
                           'execution_count': self.execution_count,
                           'payload': [], 'user_expressions': {}}

        else:
            result = {'data': {'text/plain': 'Could not connect to Neo4j'}, 
                              'execution_count': self.execution_count}
            self.send_response(self.iopub_socket, 'execute_result', result)
            exec_result = {'status': 'error', 
                           'execution_count': self.execution_count}

        return exec_result

    def do_complete(self, code, cursor_pos):
        # Got the keywords from:
        # http://neo4j.com/docs/developer-manual/current/cypher/syntax/reserved/
        space_idxs = [i for i, l in enumerate(code) if l == ' ']
        low_idxs = [s for s in space_idxs if s < cursor_pos]
        if low_idxs:
            low_cp = max([s for s in space_idxs if s < cursor_pos]) + 1
            key_start = code[low_cp:cursor_pos]
        else:
            low_cp = 0
            key_start = code[:cursor_pos]

        matches = [k for k in self.keywords if k.startswith(key_start)] + [str(cursor_pos)]
        content = {'matches' : matches, 'cursor_start' : low_cp, 
                   'cursor_end' : cursor_pos, 'metadata' : {}, 'status' : 'ok'}
        return content