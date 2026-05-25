.PHONY: compile fixture smoke-test clean-fixtures
compile:
	python -m compileall config src scripts
fixture:
	python scripts/create_fixture_excel.py
smoke-test: clean-fixtures fixture
	python scripts/run_pipeline.py \
		--raw-dir tests/fixtures/raw \
		--output-dir tests/fixtures/processed \
		--input-file Demographic-aspects-2023.xlsx \
		--output-file demographic_aspects_2023.csv
	test -s tests/fixtures/processed/demographic_aspects_2023.csv
clean-fixtures:
	rm -rf tests/fixtures
