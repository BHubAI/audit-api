"""Defines the infrastructure pieces for the API Template."""

from aws_cdk import CfnParameter, aws_secretsmanager
from bhub_cdk.stack import ApplicationNestedStack
from constructs import Construct


class SecretsStack(ApplicationNestedStack):
    sample_secret = aws_secretsmanager.ISecret

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        sample_secret_parameter: CfnParameter,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.sample_secret = self._get_or_create_secret(
            "APITemplateSampleSecret",
            secret_string=sample_secret_parameter.value_as_string,
        )

    def _get_or_create_secret(
        self,
        secret_name: str,
        secret_string: str = None,
    ) -> aws_secretsmanager.Secret:
        secret = aws_secretsmanager.Secret(self, secret_name)
        cfn_secret = secret.node.default_child
        if cfn_secret and secret_string:
            cfn_secret.secret_string = secret_string
            cfn_secret.generate_secret_string = None

        return secret
