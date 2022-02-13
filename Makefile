.PHONY: test
test:
	PYTHONPATH=. pytest -vrP --cov-report=term-missing --cov=okdmr.dmrlib
