# from distutils.core import setup
from setuptools import setup


with open('README.md') as f:
    readme = f.read()

setup(
    name='cypher_kernel',
    version='0.1',
    packages=['cypher_kernel'],
    description='Simple Cypher kernel for Jupyter',
    long_description=readme,
    author='HelgeCPH',
    author_email='rhp@cphbusiness.dk',
    url='https://github.com/HelgeCPH/cypher_kernel',
    install_requires=[
        'jupyter_client', 'IPython', 'ipykernel', 'requests', 'jinja2'
    ],
    include_package_data=True,
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
    ],
)
