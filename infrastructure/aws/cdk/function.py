from __future__ import annotations

from datetime import datetime

import aws_cdk.aws_cloudwatch as cloudwatch
import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_events as events
import aws_cdk.aws_events_targets as events_targets
import aws_cdk.aws_kms as kms
import aws_cdk.aws_lambda as lambda_
import aws_cdk.aws_secretsmanager as secretsmanager
from aws_cdk import Duration, Stack, Tags
from aws_cdk import aws_lambda_event_sources as event_sources
from aws_cdk.aws_lambda import Function as AwsPythonFunction
from bhub_cdk.common import BusinessUnit
from bhub_cdk.constants import DATADOG_SITE
from bhub_cdk.ssm import SharedParameters
from bhub_cdk.vpc import PrivateSubnets, Vpc
from constructs import Construct

from infrastructure.aws.cdk.sqs import Sqs

DATADOG_LAMBDA_HANDLER = "datadog_lambda.handler.handler"


class Lambda(AwsPythonFunction):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        handler: str,
        business_unit: BusinessUnit = None,
        memory_size: int = 128,
        timeout: int = 30,
        **kwargs,
    ) -> None:
        """Creates a Python lambda inside BHub's shared VPC.

        Parameters
        ----------
        scope : Construct
        construct_id: str
        business_unit : BusinessUnit or None
            The business unit that this AWS Lambda belongs to or `None`. It's mandatory
            if the parent stack doesn't have the attribute `BUSINESS_UNIT`.
        **kwargs
            The same parameters to build a new instance of
            `aws_cdk.aws_lambda_python_alpha.PythonFunction`.

        Raises
        ------
        ValueError
            When neither parent stack's `BUSINESS_UNIT` is set and `business_unit` is
            None.
        """
        stack = Stack.of(scope)
        kwargs["vpc"] = Vpc.shared(scope)
        stack_business_unit = getattr(stack, "BUSINESS_UNIT", None)

        if stack_business_unit:
            kwargs["vpc_subnets"] = PrivateSubnets.select_for(
                scope, stack_business_unit
            )
        elif business_unit:
            kwargs["vpc_subnets"] = PrivateSubnets.select_for(scope, business_unit)
        else:
            raise ValueError(
                "Parameter `business_unit` is mandatory without specifying"
                " `BUSINESS_UNIT` in the parent stack"
            )
        if kwargs["environment"] is None:
            kwargs["environment"] = {}

        filesystem = kwargs.pop("filesystem", None)

        if filesystem:
            kwargs["filesystem"] = self._add_filesystem(construct_id, filesystem)

        lambda_build_args = {"--platform": "linux/amd64"}

        if "from_asset" in kwargs:
            lambda_code = lambda_.Code.from_asset(kwargs.pop("from_asset"))
            kwargs["runtime"] = lambda_.Runtime.PYTHON_3_11
            kwargs["handler"] = handler
        else:
            lambda_code = lambda_.Code.from_asset_image(
                "./",
                build_args=lambda_build_args,
                entrypoint=["python", "-m", "awslambdaric"],
                cmd=[DATADOG_LAMBDA_HANDLER],
            )
            kwargs["runtime"] = lambda_.Runtime.FROM_IMAGE
            kwargs["handler"] = lambda_.Handler.FROM_IMAGE
            kwargs.pop("layers", None)

        kwargs["architecture"] = lambda_.Architecture.X86_64
        kwargs["memory_size"] = memory_size
        kwargs["timeout"] = Duration.seconds(timeout)
        kwargs["code"] = lambda_code

        secrets = kwargs.get("secrets", {}) or {}
        key_managements = kwargs.get("key_managements", {})
        kwargs.pop("secrets", False)
        kwargs.pop("key_managements", False)

        super().__init__(scope, construct_id, **kwargs)

        self._setup_datadog(scope, handler)

        for key, value in secrets.items():
            self.add_secret(key, value)

        for key, value in key_managements.items():
            self.add_kms(key, value)

    def add_secret(
        self, environment_var_name: str, secret: secretsmanager.Secret
    ) -> None:
        """Make secret accessible by the lambda exporting its ARN as env var.

        Parameters
        ----------
        environment_var_name : str
            The desired name for the environment variable to be created.
        secret : secretsmanager.Secret
            The secret that is going to be used inside the Lambda.
        """
        secret.grant_read(self)
        self.add_environment(environment_var_name, secret.secret_arn)

    def add_kms(self, environment_var_name: str, key_management: kms.Key) -> None:
        """Make secret accessible by the lambda exporting its ARN as env var.

        Parameters
        ----------
        environment_var_name : str
            The desired name for the environment variable to be created.
        key_management : kms.Key
            The KMS key that is going to be used inside the Lambda.
        """
        key_management.grant_encrypt_decrypt(self)
        self.add_environment(environment_var_name, key_management.key_arn)

    def add_sqs_trigger(self, sqs: Sqs, *, batch_size: int | None = None) -> None:
        """Adds an SQS trigger to the lambda.

        Parameters
        ----------
        queue : aws_cdk.aws_sqs.Queue
            The queue that will trigger the lambda.
        """
        sqs.grant_consume(self)
        event_source = event_sources.SqsEventSource(sqs.queue, batch_size=batch_size)

        self.add_event_source(event_source)

    def connection_allow_to_default_port(
        self, connectable: ec2.IConnectable, description: str = None
    ):
        """Allow connections to the security group on their default port."""
        self.connections.allow_to_default_port(connectable, description)

    def _setup_datadog(self, scope, handler: str):
        datadog_api_key_secret_arn = SharedParameters.datadog_api_key_secret_arn(scope)
        service_name = getattr(scope, "SERVICE_NAME", None)  # type: ignore
        account_id = Stack.of(scope).account
        application_version = datetime.now().strftime("%Y.%m.%d.%H.%M")

        Tags.of(self).add("service", service_name)
        Tags.of(self).add("env", account_id)

        datadog_environment = {
            "DD_ENV": f"aws.account.{account_id}",
            "DD_VERSION": application_version,
            "DD_SITE": DATADOG_SITE,
            "DD_TRACE_ENABLED": "true",
            "DD_SERVICE": service_name,
            "DD_LAMBDA_HANDLER": handler,
        }

        if "dummy" not in datadog_api_key_secret_arn:
            secret = secretsmanager.Secret.from_secret_complete_arn(
                self,
                "DatadogApiKeySecret",
                secret_complete_arn=datadog_api_key_secret_arn,
            )

            for key, value in datadog_environment.items():
                self.add_environment(key, value)

            self.add_secret("DD_API_KEY_SECRET_ARN", secret)


class LambdaUpdatedTrigger(Construct):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        function: lambda_.Function,
    ):
        """Triggers the given Lambda when its code is updated.

        Although CloudFormation is not a orchestration tool, it has some useful events
        that make some possible.
        One of them is the CloudTrail's `UpdateFunctionCode20150331v2`, that is sent
        every time a Lambda has its code updated. This construct makes use of this
        event to trigger the given lambda.

        Parameters
        ----------
        scope : Construct
            The parent Stack or Construct context of this construct.
        construct_id : str
            An unique ID (inside of the given scope) for this construct.
        function : lambda_.Function
            The lambda that is going to be executed when its code gets updated.
        """
        super().__init__(scope, construct_id)

        rule = events.Rule(
            self,
            f"APITemplateLambdaTrigger-{construct_id}",
            description="Trigger lambda after in a given frequency",
            event_pattern=events.EventPattern(
                account=[Stack.of(self).account],
                source=["aws.lambda"],
                detail={
                    "eventSource": ["lambda.amazonaws.com"],
                    "eventName": [
                        "UpdateFunctionCode20150331v2",
                    ],
                    "responseElements": {"functionArn": [function.function_arn]},
                },
            ),
        )

        rule.add_target(events_targets.LambdaFunction(function))

        metric = function.metric_errors()

        cloudwatch.Alarm(
            self,
            f"LambdaTriggerError-{construct_id}",
            metric=metric,
            evaluation_periods=1,
            threshold=1,
        )
