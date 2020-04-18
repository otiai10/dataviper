.DEFAULT_GOAL := default

default: clean build

build:
	python setup.py sdist

clean:
	rm -rf dist

release:
	twine upload dist/*

