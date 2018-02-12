# Related Work

## Official Documentation for writing Wrapper Kernels

[http://jupyter-client.readthedocs.io/en/latest/wrapperkernels.html](http://jupyter-client.readthedocs.io/en/latest/wrapperkernels.html)

For this Cypher kernel, I started with modifying the Echo kernel, see [https://github.com/jupyter/echo_kernel](https://github.com/jupyter/echo_kernel). 


## `pexpect.replwrap.REPLWrapper`

Originally, I wanted to wrap the `cypher-shell` with the `replwrap` module, see
[https://pexpect.readthedocs.io/en/stable/api/replwrap.html](https://pexpect.readthedocs.io/en/stable/api/replwrap.html), which uses `Pexpect`, see [https://pexpect.readthedocs.io/en/latest/](https://pexpect.readthedocs.io/en/latest/).

However, when starting the REPL via: 

```
cypher-shell -u neo4j -p pwd --format plain --debug
```

the REPL does not seem to provide any option for printing the `<_id>` field of nodes and edges. That is an issue for visualizing, when it is important 


```
neo4j> MATCH (a)-[:HAS]-(c) RETURN a;
a
(:Bike {weight: 10})
(:Bike {weight: 10})
(:Wheel {spokes: 3})
(:Wheel {spokes: 32})
(:Bike {weight: 10})
(:Bike {weight: 10})
(:Wheel {spokes: 3})
(:Wheel {spokes: 32})
```

The way to wrap the `cypher-shell` REPL could be as in teh following:

```python
from pexpect.replwrap import REPLWrapper
cypher = REPLWrapper("cypher-shell -u neo4j -p pwd", "neo4j> ", None)
cypher.run_command("""MATCH (a)-[:HAS]-(c) RETURN a;;""")
```

However, the output here is as incomplete as above woth respect to the ID of the graph elements.

```python
'\x1b[mMATCH (a)-[:HAS]-(c) RETURN a;;\r\r\n+-----------------------+\r\n| a                     |\r\n+-----------------------+\r\n| (:Bike {weight: 10})  |\r\n| (:Bike {weight: 10})  |\r\n| (:Wheel {spokes: 3})  |\r\n| (:Wheel {spokes: 32}) |\r\n+-----------------------+\r\n\r\n4 rows available after 94 ms, consumed after another 20 ms\r\n\x1b[31mInvalid input \';\': expected <init> (line 1, column 1 (offset: 0))\r\n";"\r\n ^\x1b[m\r\n\x1b[1m'
```

Consider writing a question to: [https://github.com/neo4j/cypher-shell/issues](https://github.com/neo4j/cypher-shell/issues) to see if the query output could be made more complete.



## `py2neo`

Nicole White's blog entry shows how to use `py2neo` [http://py2neo.org/v3/](http://py2neo.org/v3/) to work with Neo4j in Jupyter notebooks, see [https://nicolewhite.github.io/neo4j-jupyter/hello-world.html](https://nicolewhite.github.io/neo4j-jupyter/hello-world.html). Additionally, it includes Python code, which generates a vis.js network for the entire Neo4j graph, see [https://github.com/nicolewhite/neo4j-jupyter/blob/master/scripts/vis.py](https://github.com/nicolewhite/neo4j-jupyter/blob/master/scripts/vis.py).

## `ipython-cypher`

Similarly, there is an implementation of `%%cypher` magic for Jupyter notebooks, see [https://github.com/versae/ipython-cypher/blob/master/src/cypher/run.py](https://github.com/versae/ipython-cypher/blob/master/src/cypher/run.py). This tool focuses on integrating Cypher query results with Python code.

## Neo4j HTTP API

Since, I can get hold of graph element IDs via the HTTP API, I decided to wrap this one. The code for the `requests` POST requests is based on [https://neo4j.com/docs/developer-manual/3.4-preview/http-api/](https://neo4j.com/docs/developer-manual/3.4-preview/http-api/) and on [https://neo4j.com/docs/developer-manual/3.4-preview/http-api/authentication/](https://neo4j.com/docs/developer-manual/3.4-preview/http-api/authentication/).


## Alchemy.js


http://graphalchemist.github.io/Alchemy/#/
http://graphalchemist.github.io/Alchemy/#/examples



### Getting Help on JavaScript-based Visualizations

Since I do not know how to do this properly, I was asking in Jupyter's general help center [https://github.com/jupyter/help](https://github.com/jupyter/help/issues/296). My question is here: [https://github.com/jupyter/help/issues/296](https://github.com/jupyter/help/issues/296).

