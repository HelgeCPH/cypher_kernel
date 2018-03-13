# Cypher Kernel

This is a small Jupyter kernel wrapping the Cypher language and Neo4j [https://neo4j.com/developer/cypher/](https://neo4j.com/developer/cypher/).

![](docs/what_is_this.gif)


## Why? Do I need a Cypher language kernel?

I started working on this kernel as I am teaching on Cypher and Neo4j as part of a database course on Copenhagen Business Academy.

Usually, my lecture notes are in Jupyter notebooks and I use the Jupter extension [RISE](https://github.com/damianavila/RISE) to make slideshows with executable code.

In the classes on graph databases, I want to focus on the query language Cypher. That is, I do not want to have Cypher embedded in Python such as with [icypher](https://github.com/lebedov/icypher) -a `%cypher` magic sending queries with the help of `py2neo`- or in [plain Python notebooks](https://nicolewhite.github.io/neo4j-jupyter/hello-world.html)


## How does it look like?

In case you do not have a Python environment with Jupyter installed on your system, you can see in the following how the rendered notebooks -not the presentations- could look like, see:

  * https://nbviewer.jupyter.org/github/HelgeCPH/cypher_kernel/blob/master/example/paradise_papers.ipynb
  * https://nbviewer.jupyter.org/github/HelgeCPH/cypher_kernel/blob/master/example/movie_graph.ipynb or
  * http://htmlpreview.github.io/?https://github.com/HelgeCPH/cypher_kernel/blob/master/example/movie_graph.html 



## Installation

To install the `cypher_kernel` from PyPi:

```bash
pip install cypher_kernel
python -m cypher_kernel.install
```

To work on this code directly, you may want to:

```bash
git clone git@github.com:HelgeCPH/cypher_kernel.git
cd cypher_kernel
python setup.py install
pip install .
python -m cypher_kernel.install
```

## Configuration

To configure a Neo4j user, password, and the address of the Neo4j REST API, you can specify the values in the configuration file `cypher_config.yml`. Normally, this file is located under `~/.jupyter/`. In case the file is not existent the following default configuration is used:

```yaml
user: 'neo4j'
pwd: 'neo4j'
host: 'localhost:7474'
connect_result_nodes: False
cmd_timeout: null
```


## Using the Cypher Kernel

**Notebook**: The *New* menu in the notebook should show an option for an `Cypher` notebook.

**Console frontends**: To use it with the console frontends, add `--kernel cypher` to their command line arguments.



## Neo4j for Presentations


To get quickly started -under the assumption you have Docker installed- start up a Neo4j DBMS instance with: 

```bash
docker run --rm --publish=7474:7474 --publish=7687:7687 neo4j
docker run --rm --publish=7474:7474 --publish=7687:7687 --env=NEO4J_dbms_memory_pagecache_size=4G neo4j
```

  * Navigate with your browser to http://localhost:7474
  * Login with `neo4j` as username and password respectively
  * Change the password to a new one. **OBS** Do not forget to add this password to the `cypher_config.yml`, see above.
  * Now, create a new Cypher notebook.

See more on configuring the Neo4j container https://neo4j.com/docs/operations-manual/current/installation/docker/


### What? I have Docker but no `pip` and other Python stuff?!

Likely the easiest way to get started, have:

  * A Linux/OS X (Windows should work but I cannot test it at the moment...)
  * An installation of Anaconda (with Python 3.6), see https://www.anaconda.com/download/. Download and install it according to their documentation, see https://docs.anaconda.com/anaconda/install/
  * A Docker installation, see https://www.docker.com/community-edition#/download. Alternatively, a native installation of Neo4j, see https://neo4j.com/download/
  * The `cypher_kernel`:
  ```bash
  pip install cypher_kernel
  python -m cypher_kernel.install
  ```
  * The Jupyter Notebook server up and running:
  ```bash
  jupyter notebook
  ```

That should be it...


