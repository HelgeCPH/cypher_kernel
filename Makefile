.PHONY: init test build install devinst

build:
	python setup.py install

devinst: build
	pip install . --upgrade --no-deps

install:
	pip install .

test:
	py.test -s tests

publish:
	python setup.py sdist
	twine upload dist/cypher_kernel-*.tar.gz

clean:
	rm -r build/;rm -r .cache;rm -r cypher_kernel.egg-info;rm dist/*