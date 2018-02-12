# Cypher Kernel

This is a small Jupyter kernel wrapping the Cypher language and Neo4j [https://neo4j.com/developer/cypher/](https://neo4j.com/developer/cypher/).


## Installation

To install the `cypher_kernel`:

```bash
git clone git@github.com:HelgeCPH/cypher_kernel.git
cd cypher_kernel
python setup.py install
python -m cypher_kernel.install
```

## Using the Cypher Kernel

**Notebook**: The *New* menu in the notebook should show an option for an `Cypher` notebook.

**Console frontends**: To use it with the console frontends, add `--kernel cypher` to their command line arguments.


## Configuration

To configure a Neo4j user, password, and the address of the Neo4j REST API, you can specify the values in the configuration file `cypher_config.yml`. Normally, this file is located under `~/.jupyter/`. In case the file is not existent the following default configuration is used:

```yaml
user: 'neo4j'
pwd: 'neo4j'
host: 'localhost:7474'
connect_result_nodes: False
```


## Neo4j for Presentations


To get quickly started -under the assumption you have Docker installed- start up a Neo4j DBMS instance with 

```bash
docker run --rm --publish=7474:7474 --publish=7687:7687 neo4j
```

  * Navigate with your browser to http://localhost:7474
  * Login with `neo4j` as username and password respectively
  * Change the password to a new one. **OBS** Do not forget to add this password to the `cypher_config.yml`, see above.
  * Now, create a new Cypher notebook.
