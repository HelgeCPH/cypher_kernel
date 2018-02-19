import re
import uuid
import yaml


class Node:
    def __init__(self, node_dict):
        self.id = int(node_dict['id'])
        self._labels = node_dict['labels']
        self.label = self._labels[0]
        self.properties = str(node_dict['properties'])
        self.properties_dict = node_dict['properties']
        properties_long = dict(node_dict['properties'])
        properties_long['_id'] = self.id
        self.properties_long = '{'
        for k, v in properties_long.items():
            if type(v) == str and "'" in v:
                v.replace("'", "\'")
                # v.replace('"', '\"')
            self.properties_long += k + ':' + str(v) + ', '
        self.properties_long = self.properties_long[:-1] + '}'

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
        properties_long = dict(rel_dict['properties'])
        properties_long['_id'] = self.id
        self.properties_long = '{'
        for k, v in properties_long.items():
            if type(v) == str and "'" in v:
                v.replace("'", "\'")
                # v.replace('"', '\"')
            self.properties_long += k + ':' + str(v) + ', '

        # TODO: Check how to avoid escaping the " in the following
        self.properties_long = (self.properties_long[:-1] + '}').replace('"', '\\"')
    
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


def parse_path(content: str) -> (list, list):
    # TODO: Add error handling in case of no matches...
    nodes = []
    rels = []

    # Make splitting on edges save. Splitting on `-` is not save. It appears 
    # to often in data, e.g., the movie graph.
    edge_uuid = str(uuid.uuid4())[:10]
    content = re.sub("\)<?-\[", f')-{edge_uuid}-[', content)
    content = re.sub("\]->?\(", f']-{edge_uuid}-(', content)

    for el in content.split(f'-{edge_uuid}-'):
        field = el.lstrip('>').rstrip('<')
        print(field)
        if field[0] == '(' and field[-1] == ')':
            node = parse_node(field)
            print(node.id)
            nodes.append(node)
        elif field[0] == '[' and field[-1] == ']':
            rels.append(parse_relation(field))

    return nodes, rels


def parse_node(content):
    # TODO: check if there can be many labels and how they are 
    # remove prenthesis
    # (:Bike {weight: 10, _id_: 58})
    regex = '\(:(?P<label>\w+) \{(?P<props>.*)\}\)'
    match = re.match(regex, content)
    
    # TODO: Add error handling in case of no matches...
    # TODO: Check if a relation can have multiple types...
    label = match.group('label')
    props_str = match.group('props')

    node_dict = {'id': None, 'labels': [label], 'properties': None}

    # Found that YAML can parse JS style dictionaries, 
    # see https://stackoverflow.com/a/38066510 The nice thing is that it 
    # parses types of values too!
    prop_dict = yaml.load('{' + props_str + '}')
    node_dict['id'] = prop_dict['_id_']
    del prop_dict['_id_']
    node_dict['properties'] = prop_dict

    return Node(node_dict)

def parse_relation(content):
    # [:HAS {_id_: 36, position: 2}[58>60]]
    regex = '\[:(?P<label>\w+) \{(?P<props>.*)\}\[(?P<source>\d+)>(?P<target>\d+)\]'
    match = re.match(regex, content)
    
    # TODO: Add error handling in case of no matches...
    # TODO: Check if a relation can have multiple types...
    label = match.group('label')
    props_str = match.group('props')
    source = match.group('source')
    target = match.group('target')

    rel_dict = {'id': None, 'type': label, 'properties': None, 
                'startNode': source, 'endNode': target}

    # prop_dict = {}
    # for p in props_str.split(', '):
    #     name, value = p.split(': ')   
    #     if name == '_id_':
    #         rel_dict['id'] = value
    #         continue
    #     if value.startswith('"'):
    #         # If the value is a string in Java, just remove the "
    #         value = value.replace('"', '')
    #     else:
    #         try:
    #             value = int(value)
    #         except:
    #             try:
    #                 value = float(value)
    #             except:
    #                 pass
    #     prop_dict[name] = value

    prop_dict = yaml.load('{' + props_str + '}')
    rel_dict['id'] = prop_dict['_id_']
    del prop_dict['_id_']
    rel_dict['properties'] = prop_dict

    return Relation(rel_dict)

def parse_value(content):
    return content

# case: output is an error
def parse_error(code):
    # TODO: check if the ANSI codes have to get removed...
    return code

def parse_success(code):
    nodes = []
    relations = []

    columns = code[0].strip('|').split('|')
    runtime = code[-1]
    for line in code[2:-3]:
        # remove leading and trailing '|' and split into fields
        # OBS: this assumes that there are no '|' in the graph entities!
        fields = [f.strip() for f in line.strip('|').split('|')]
        for field in fields:
            if (')-[' in field) or (')->[' in field) or (')<-[' in field):
                # it is a path
                loc_nodes, loc_rels = parse_path(field)

                nodes += loc_nodes
                relations += loc_rels
            elif field[0] == '(' and field[-1] == ')':
                node = parse_node(field)
                nodes.append(node)
            elif field[0] == '[' and field[-1] == ']':
                rel = parse_relation(field)
                relations.append(rel)
            # I do not need this here as all the parsing is only done for the 
            # visualizations
            # else:
            #     val = parse_value(field)

    return set(nodes), set(relations)


def find_start_of_output(output):
    for idx, line in enumerate(output):
        if line.startswith('+---'):
            return idx + 1
    return 0


def parse_output(output: list) -> (str, tuple):
    # Reduce to the part of the output containing information
    res = output[find_start_of_output(output):-1]

    error = None
    parsing_result = (set([]), set([]))
    if output[3].startswith('\x1b[31m'):
        # TODO: check if this is the only indicator for an error
        error = parse_error(res)
    elif len(output) == 4:
        # That is, there is only the line with the runtime but no other result
        pass
    else:
        parsing_result = parse_success(res)

    return error, parsing_result


def parse_output_str(output: str) -> (str, tuple):
    return parse_output(output) 
