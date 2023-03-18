.PHONY: test
test:
	python -m coverage erase
	PYTHONPATH=. pytest -vrP --cov-report=term-missing --cov=okdmr.dmrlib --cov-report=xml
