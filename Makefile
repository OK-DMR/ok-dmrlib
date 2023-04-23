.PHONY: test
test:
	python -m coverage erase
	PYTHONPATH=. pytest -vrP --cov-report=term-missing --cov=okdmr.dmrlib --cov-report=xml

clean:
	git clean -xdff

release:
	python3 -m build . --sdist --wheel
