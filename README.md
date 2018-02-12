# Cypher Kernel

This is a small Jupyter kernel wrapping the Cypher language and Neo4j [https://neo4j.com/developer/cypher/](https://neo4j.com/developer/cypher/).


## Installation

To install the `cypher_kernel`:

```bash
git clone
cd cypher_kernel
python setup.py install
python -m cypher_kernel.install
```

## Using the Cypher Kernel

**Notebook**: The *New* menu in the notebook should show an option for an `Cypher` notebook.

**Console frontends**: To use it with the console frontends, add `--kernel cypher` to their command line arguments.
