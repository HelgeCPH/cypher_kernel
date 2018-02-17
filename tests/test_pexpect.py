import os
import pytest
import platform
import tests.test_cfg as test_cfg
from .context import cypher_kernel as ck
from pexpect.replwrap import REPLWrapper


@pytest.fixture
def cypher_shell():
    if platform == 'Windows':
        cypher_shell_bin = os.path.join('cypher_kernel', 'java', 
                                        'cypher-shell.bat')
    else:
        cypher_shell_bin = 'cypher_kernel/java/cypher-shell'
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cypher_shell_bin = os.path.join(base_path, cypher_shell_bin)
    cypher = REPLWrapper(f'{cypher_shell_bin} -u {test_cfg.user} -p {test_cfg.pwd} --format verbose', 'neo4j> ', None)
    return cypher


def test_delete(cypher_shell):
    query = "MATCH (n) DETACH DELETE n;"
    res = cypher_shell.run_command(query)
    print(res)

def test_match_on_empty_db(cypher_shell):
    query = "MATCH (n) RETURN n;"
    res = cypher_shell.run_command(query)
    line_response = res.splitlines()
    print('#################################')
    print(res)
    print(line_response)
    print('#################################')
    error, parse_result = ck.cypher_utils.parse_output(line_response)
    assert not error
    assert parse_result == (set([]), set([]))

def test_create_graph(cypher_shell):
    query = """CREATE ( bike:Bike { weight: 10 } ) 
CREATE ( frontWheel:Wheel { spokes: 3 } ) 
CREATE ( backWheel:Wheel { spokes: 32 } ) 
CREATE p1 = (bike)-[:HAS { position: 1 } ]->(frontWheel) 
CREATE p2 = (bike)-[:HAS { position: 2 } ]->(backWheel) 
RETURN bike, p1, p2;"""

    # TODO: Figure out how to handle multiline queries properly!
    # I have the imporession that you cannot do that with `run_command` from 
    # the REPLWrapper. Likely it has to be done as in the following:
    #
    # p = pexpect.spawn('/bin/ls')
    # ...: p.expect(pexpect.EOF)
    # ...: print(p.before)
    #
    # see: http://pexpect.readthedocs.io/en/stable/api/pexpect.html#spawn-class
    query = ' '.join(query.splitlines())
    res = cypher_shell.run_command(query)
    print(res)


@pytest.mark.skip(reason="Feel like it at the moment...")
def test_match_all_nodes(cypher_shell):
    query = "MATCH (n) RETURN n;"
    res = cypher_shell.run_command(query)
    # TODO: put this in a regular expression
    assert res.startswith('\x1b[mMATCH (n) RETURN n;\r\r\n+----------------------------------+\r\n| n                                |\r\n+----------------------------------+\r\n')
    assert '| (:Bike {weight: 10, _id_: ' in res
    assert '})  |\r\n| (:Wheel {spokes: 3, _id_: ' in res
    assert '})  |\r\n| (:Wheel {spokes: 32, _id_: ' in res
    assert '}) |\r\n+----------------------------------+\r\n\r\n3 rows available after' in res


def test_parse_match_all_nodes(cypher_shell):
    query = "MATCH (n) RETURN n;"
    res = cypher_shell.run_command(query).splitlines()
    line_response = res
    error, parse_result = ck.cypher_utils.parse_output(line_response)
    assert not error
    nodes, relations = parse_result
    # TODO: make this perhaps a test, which compares the nodes properly
    assert len(nodes) == 3