all: clean-pyc test

vm-start:
	cd tests && vagrant up

docs:
	cd docs && make html

test:
	python setup.py nosetests --stop --tests tests.py

dev-test:
	GOTTWALL_REDIS_HOST=127.0.0.1 python setup.py test

travis:
	python setup.py test

coverage:
	python setup.py nosetests  --with-coverage --cover-package=stati --cover-html --cover-html-dir=coverage_out coverage


shell:
	../venv/bin/ipython

audit:
	python setup.py autdit

build:
	python setup.py sdist

version := $(shell sh -c "grep -oP 'VERSION = \"\K[0-9\.]*?(?=\")' ./setup.py")

release:
	git tag -f v$(version) && git push upstream --tags
	python setup.py sdist upload

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

find-print:
	grep -r --include=*.py --exclude-dir=venv --exclude=fabfile* --exclude=tests.py --exclude-dir=tests --exclude-dir=commands 'print' ./

activate:
	. venv/bin/activate

env:
	./env.sh dev_py
	. venv/bin/activate

aggregator-debug:
	python gottwall --config=examples/example1.py aggregator start --reload --logging=debug
