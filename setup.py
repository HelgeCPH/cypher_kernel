# from distutils.core import setup
import cypher_kernel
from setuptools import setup


with open('README.md') as f:
    readme = f.read()

setup(
    name='cypher_kernel',
    version=cypher_kernel.__version__,
    packages=['cypher_kernel'],
    description='A Cypher kernel for Jupyter',
    long_description=readme,
    author='HelgeCPH',
    author_email='rhp@cphbusiness.dk',
    url='https://github.com/HelgeCPH/cypher_kernel',
    install_requires=[
        'jupyter_client', 'IPython', 'ipykernel', 'requests', 'jinja2'
    ],
    include_package_data=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Education',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3',
    ],
)
