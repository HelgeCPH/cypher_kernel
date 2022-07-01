# from distutils.core import setup
import cypher_kernel
from setuptools import setup

setup(
    name="cypher_kernel",
    version=cypher_kernel.__version__,
    packages=["cypher_kernel"],
    description="A Cypher kernel for Jupyter",
    long_description="""Cypher Kernel
=============

This is a Cypher kernel for Jupyter notebooks.

Installation
------------

To install the ``cypher_kernel`` from PyPI:

.. code:: bash

   pip install cypher_kernel
   python -m cypher_kernel.install


Dependencies
~~~~~~~~~~~~

The kernel requires a Neo4j database engine running somewhere. For experimentation and under the assumption that Docker is installed, an instance can be spawned as in the following:

.. code:: bash

   docker run \
       --rm \
       --publish=7474:7474 \
       --publish=7687:7687 \
       --env NEO4J_AUTH=neo4j/pwd \
       neo4j



Configuration
-------------

The Cypher Kernel needs to know to which Neo4j instance to connect, which can be specified in ``~/.jupyter/cypher_config.yml``. In case the file is not existent the following default
configuration is used:

.. code:: yaml

   user: 'neo4j'
   pwd: 'pwd'
   host: 'neo4j://localhost:7687'
   connect_result_nodes: False
   cmd_timeout: null

Using the Cypher Kernel
-----------------------

**Notebook**: The *New* menu in the notebook should show an option for
an ``Cypher`` notebook.
    """,
    author="HelgeCPH",
    author_email="ropf@itu.dk",
    url="https://github.com/HelgeCPH/cypher_kernel",
    install_requires=["jupyter_client==5.2.2", "IPython", "ipykernel", "requests", "jinja2", "pyyaml", "neo4j"],
    include_package_data=True,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3",
    ],
)
