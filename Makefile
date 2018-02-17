.PHONY: init test build install devinst

build:
	python setup.py install

devinst:
	pip install . --upgrade

install:
	pip install . 

test:
    py.test -s tests

clean:
	rm -r build/;rm -r .cache;rm -r cypher_kernel.egg-info