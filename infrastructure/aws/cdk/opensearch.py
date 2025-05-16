import aws_cdk as cdk
from aws_cdk import CfnOutput, Stack
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_iam
from aws_cdk import aws_iam as iam
from aws_cdk import aws_opensearchservice as oss
from aws_cdk.aws_opensearchservice import Domain, TLSSecurityPolicy
from constructs import Construct


class OpenSearchStack(cdk.NestedStack):  # type: ignore[misc]
    def __init__(  # type: ignore[no-untyped-def]
        self,
        scope: Construct,
        construct_id: str,
        vpc: ec2.IVpc,
        subnets: ec2.SubnetSelection,
        **kwargs,
    ) -> None:  #
        super().__init__(scope, construct_id, **kwargs)

        self._set_opensearch_security_group(vpc)

        domain = self._get_domain(vpc, subnets)

        self._set_pipeline_role(domain)

        cdk.CfnOutput(
            self,
            "RoleName",
            value=self.iam_role.role_name,
            export_name=f"{self.stack_name}-RoleName",
        )
        cdk.CfnOutput(
            self,
            "RoleArn",
            value=self.iam_role.role_arn,
            export_name=f"{self.stack_name}-RoleArn",
        )

        CfnOutput(
            self,
            "OpenSearchDomainHost",
            value=domain.domain_endpoint,
        )

    def _set_pipeline_role(self, domain: Domain) -> None:
        region = Stack.of(self).region
        account_id = Stack.of(self).account
        open_search_integration_pipeline_iam_role = aws_iam.PolicyDocument()
        open_search_integration_pipeline_iam_role.add_statements(
            aws_iam.PolicyStatement(
                **{
                    "effect": aws_iam.Effect.ALLOW,
                    "resources": [f"arn:aws:es:{region}:{account_id}:domain/*"],
                    "actions": ["es:DescribeDomain"],
                }
            )
        )

        open_search_integration_pipeline_iam_role.add_statements(
            aws_iam.PolicyStatement(
                **{
                    "effect": aws_iam.Effect.ALLOW,
                    "resources": [domain.domain_arn],
                    "actions": ["es:ESHttp*"],
                }
            )
        )

        pipeline_role = aws_iam.Role(
            self,
            "OpenSearchIngestionPipelineRole",
            role_name="OpenSearchDomainPipelineRole",
            assumed_by=aws_iam.ServicePrincipal("osis-pipelines.amazonaws.com"),
            inline_policies={
                "domain-pipeline-policy": open_search_integration_pipeline_iam_role  # noqa
            },
        )
        self.iam_role = pipeline_role

        pipeline_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonDynamoDBFullAccess")
        )
        pipeline_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess")
        )

    def _get_domain(self, vpc: ec2.IVpc, subnets: ec2.SubnetSelection) -> Domain:
        single_subnet_selection = self._get_single_subnet_selection(subnets)
        domain = Domain(
            self,
            "DocumentsOssDomain",
            version=oss.EngineVersion.OPENSEARCH_2_11,
            encryption_at_rest=oss.EncryptionAtRestOptions(enabled=True),
            node_to_node_encryption=True,
            vpc=vpc,
            vpc_subnets=[single_subnet_selection],
            capacity=oss.CapacityConfig(
                data_node_instance_type="t3.small.search",
                data_nodes=1,
                multi_az_with_standby_enabled=False,
            ),
            removal_policy=cdk.RemovalPolicy.DESTROY,
            security_groups=[self.opensearch_security_group],
            tls_security_policy=TLSSecurityPolicy.TLS_1_2_PFS,
        )

        self.opensearch_domain_endpoint = domain.domain_endpoint

        domain.add_access_policies(
            iam.PolicyStatement(
                principals=[iam.AnyPrincipal()],
                actions=["es:ESHttp*"],
                effect=iam.Effect.ALLOW,
                resources=[domain.domain_arn + "/*"],
            )
        )

        return domain

    def _get_single_subnet_selection(
        self, subnets: ec2.SubnetSelection
    ) -> ec2.SubnetSelection:
        single_subnet = subnets.subnets[0] if subnets.subnets else None

        if single_subnet is None:
            raise ValueError("No subnets found in the provided SubnetSelection")

        single_subnet_selection = ec2.SubnetSelection(subnets=[single_subnet])
        return single_subnet_selection

    def _set_opensearch_security_group(self, vpc: ec2.IVpc) -> None:
        self.opensearch_security_group = ec2.SecurityGroup(
            self,
            "OpensearchSecurityGroup",
            vpc=vpc,
            allow_all_outbound=False,
            security_group_name="OpensearchSecurityGroup",
        )
        port_http = ec2.Port.tcp(80)
        port_https = ec2.Port.tcp(443)
        self.opensearch_security_group.add_ingress_rule(
            ec2.Peer.ipv4(vpc.vpc_cidr_block), port_http
        )
        self.opensearch_security_group.add_ingress_rule(
            ec2.Peer.ipv4(vpc.vpc_cidr_block), port_https
        )
