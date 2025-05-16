# AUDIT API

API to handle audit data

## Requirements

- Node.js 10.13.0 or later
- Python 3.11
- Docker
- AWS CDK 2.34.2 or later
- [aws sam cli](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-cdk-getting-started.html)

## Setup

### Installing AWS CDK

Refer to the [official documentation](https://docs.aws.amazon.com/cdk/latest/guide/getting_started.html) on how to install it in your platform, the mandatory sections are `Prerequisites` and `Install the AWS CDK`.

### Python setup

Since the lambda runtime uses Python 3.11 it's important that, your local Python installation uses the same version. You can use [pyenv](https://github.com/pyenv/pyenv) to maintain different versions of Python locally.

Create a virtualenv on MacOS and Linux:

```
python3 -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required development dependencies.

```bash
make setup-python-dependencies
```

Please, read the instructions on how to configure your local environment to use `bhub_cdk` in this [link](https://github.com/BHubAI/bhub_cdk#instala%C3%A7%C3%A3o).

Make sure you have already set up your local environment with the `bootstrap.sh` script from the following [link](https://github.com/BHubAI/dev-bootstrap#bootstrap).

After installing the dependencies you're going to need to configure some environment variables. The `.env` file has the default values for it (it shouldn't be need to change anything for now).

```
cp .env.dist .env
```

To run the application locally:

```
# you can use docker:
docker-compose up

# or run it from the terminal:
python application/api/boot_local.py
```

## Quality

This project uses [black](https://github.com/psf/black) for file formatting, [flake8](https://flake8.pycqa.org/en/latest/) for styling enforcing and [isort](https://github.com/PyCQA/isort) for sorting imports. All these tools have integrations with most of the IDEs and text editors, and will run in the pre-commit hook in git which is triggered by [pre-commit](https://pre-commit.com/).

We use [pytest](https://docs.pytest.org/en/6.2.x/) to write tests for both infrastructure and the API.

## Decisions

We use Architecture Decision Records, as [described by Michael Nygard](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions).

The ADRs are stored in the [docs/architecture/decisions](https://github.com/BHubAI/hub-account-manager-api/tree/main/docs/architecture/decisions) folder in our repository.

When a requirement specifies a software system’s quality attributes, refers to a software system’s core features, impose constraints on a software system, defines the environment in which the software system will run, it is likely to be architecturally significant. In that case, please, create a new ADR for it. In case of doubt please refer to [this article](https://en.wikipedia.org/wiki/Architecturally_significant_requirements) to make sure you're creating (or not creating) a ADR for a relevant change in the project architecture.

## Running tests

From the project root run the tests with `make test`.

## To access endpoints documentation

The documentation you're referring to is likely for an API (Application Programming Interface) that provides a set of endpoints for interacting with a service or application. APIs often come with documentation that describes how to use the available endpoints, including the expected request format, parameters, and the response format. Two common tools for generating interactive API documentation are Swagger UI (accessed via the /docs path) and ReDoc (accessed via the /redoc path).

## Deploy

For Dev environment use the workflow [Pipeline - Development](https://github.com/BHubAI/documents-manager-api/blob/main/.github/workflows/pipeline-dev.yml).
For Prod environment the workflow [Pipeline - Production](https://github.com/BHubAI/documents-manager-api/blob/main/.github/workflows/pipeline-prod.yml) is actived when a Pull Request is merged in the branch main.

or

If you can make the deploy via console you can run `make deploy-cdk profile=${aws_profile} env=${environment}`. For more information about CDK commands refer to the [official documentation](https://docs.aws.amazon.com/cdk/latest/guide/cli.html).

## Acessando Open Search (dev)

Para acessar o OpenSearch AWS dev localmente, adicione isto ao seu .ssh/config:

```json
Host oss-dev-http
    HostName ec2-3-95-217-165.compute-1.amazonaws.com
    User ec2-user
    IdentityFile <path_to_your_file.pem>
    LocalForward 8158 vpc-documentsossdom-gpc7strivedk-mxdau37egqrvm2s7igxutytxs4.us-east-1.es.amazonaws.com:80
    ExitOnForwardFailure yes
```
Em seguida, envie suas chaves públicas para o _bastion host_ usando _infrastructure-dmz_

```
make send-public-key profile=bhub-workloads-platform-dev vpc_id=vpc-0814a83b9cf0eb991
```

E execute: `ssh -N oss-dev-http`

URL do opensearch: http://localhost:8158/\_dashboards
