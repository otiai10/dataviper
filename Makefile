.DEFAULT_GOAL := default

default: clean build

build:
	python setup.py sdist

clean:
	rm -rf sdist

release:
	twine upload dist/*

