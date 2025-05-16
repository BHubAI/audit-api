.SILENT: clean test local synth
.PHONY: clean local test synth

env ?= dev
github_branch ?= $(shell git branch --show-current)

clean:
	rm -rf .aws-sam/ && rm -rf cdk.out/ && rm -rf asset.* && rm -rf __pycache__/

run-local:
	export PYTHONPATH=$(CURDIR) && python presentation/api/boot_local.py

test:
	coverage run -m pytest -vv ./ && coverage report -m

lint-fix:
	pre-commit run --all-files --hook-stage manual

deploy-cdk: clean
	@test -n "$(AWS_PROFILE)" || (echo "AWS_PROFILE is not set. Usage: make deploy AWS_PROFILE={aws_profile} env={dev|prod}"; exit 1)
	@cdk deploy 

setup-python-dependencies:
	asdf plugin-add python https://github.com/danhper/asdf-python.git
	asdf install
	python -m venv venv
	. venv/bin/activate
	find requirements/ -name "*.txt" -exec bhub-pip install -r {} \;
	pre-commit install