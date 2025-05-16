FROM public.ecr.aws/lambda/python:3.11-x86_64

COPY ./presentation ${LAMBDA_TASK_ROOT}/presentation
COPY ./config ${LAMBDA_TASK_ROOT}/config
COPY ./infrastructure ${LAMBDA_TASK_ROOT}/infrastructure
COPY ./requirements/requirements.txt ${LAMBDA_TASK_ROOT}
COPY ./alembic.ini ${LAMBDA_TASK_ROOT}

RUN  pip3 install -r ${LAMBDA_TASK_ROOT}/requirements.txt --target "${LAMBDA_TASK_ROOT}"

COPY --from=public.ecr.aws/datadog/lambda-extension:51 /opt/extensions/ /opt/extensions

USER nobody
