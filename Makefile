.PHONY: test
test:
	PYTHONPATH=. pytest -rP --cov-report=term-missing --cov=okdmr.dmrlib
