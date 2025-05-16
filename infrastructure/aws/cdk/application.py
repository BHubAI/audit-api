"""Defines the infrastructure pieces for the API Template."""

from functools import lru_cache

from aws_cdk import aws_apigateway as apigateway
from aws_cdk import aws_ec2 as ec2
from bhub_cdk.ssm import SharedParameters
from bhub_cdk.ssm.cross_account import CrossAccountSSMParameterRead
from bhub_cdk.stack import ApplicationStack
from constructs import Construct

from infrastructure.aws.cdk.dns import DnsStack
from infrastructure.aws.cdk.function import Lambda
from infrastructure.aws.cdk.opensearch import OpenSearchStack


class AuditAPIStack(ApplicationStack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        self.target_environment = scope.node.try_get_context("env")

        # DNS e VPC compartilhada
        dns_stack = DnsStack(self, "DnsStack")
        vpc = dns_stack.shared_vpc

        opensearch_stack = OpenSearchStack(
            self,
            "AuditAPIOpenSearchStack",
            vpc,
            dns_stack.shared_subnets,
        )

        environment_settings = {
            "TZ": "UTC",
            "APP_ENV": "production",
            "JWT_NAMESPACE": f"https://{SharedParameters.parent_zone_name(scope)}/",
            "OPENSEARCH_DOMAIN": opensearch_stack.opensearch_domain_endpoint,
            "OPENSEARCH_PORT": "80",
        }

        api_lambda = Lambda(
            self,
            "ApiLambda",
            environment=environment_settings,
            handler="infrastructure.aws.cdk.handlers.request_handler",
            timeout=180,
            memory_size=512,
            vpc=vpc,
            security_groups=[dns_stack.lambda_security_group],
        )

        private_api = apigateway.LambdaRestApi(
            self,
            "AuditPrivateApi",
            handler=api_lambda,
            proxy=False,
            endpoint_configuration=apigateway.EndpointConfiguration(
                types=[apigateway.EndpointType.PRIVATE]
            ),
        )

        private_api.root.add_method("ANY")
        proxy_resource = private_api.root.add_resource("{proxy+}")
        for method in ["GET", "HEAD", "POST", "DELETE", "PUT", "PATCH"]:
            proxy_resource.add_method(method, apigateway.LambdaIntegration(api_lambda))

        ec2.InterfaceVpcEndpoint(
            self,
            "ApiGatewayVpcEndpoint",
            service=ec2.InterfaceVpcEndpointService(
                name="com.amazonaws.${region}.execute-api"
            ),
            vpc=vpc,
            subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
            private_dns_enabled=True,
        )

    @lru_cache
    def _read_cross_account_parameter(
        self, target_account: str, parameter_name: str, role_name: str
    ) -> str:
        assumed_role_arn = f"arn:aws:iam::{target_account}:role/{role_name}"
        return CrossAccountSSMParameterRead(
            self,
            f"CrossAccountSSMParameter{role_name}",
            name=parameter_name,
            assumed_role_arn=assumed_role_arn,
        ).parameter_value
