.PHONY: compile fixture smoke-test clean-fixtures
compile:
	python -m compileall config src scripts
