from typing import Any

import aws_cdk as cdk
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ssm as ssm
from bhub_cdk.vpc import Vpc
from constructs import Construct


class DnsStack(cdk.NestedStack):  # type: ignore[misc]
    def __init__(self, scope: Construct, construct_id: str, **kwargs: Any) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.shared_vpc = Vpc.shared(self)
        param_value = ssm.StringParameter.value_from_lookup(
            self, "/shared/network/subnet/finvis-private-subnets"
        )

        subnet_ids = param_value.split(",")

        self.shared_subnets = ec2.SubnetSelection(
            subnets=[
                ec2.Subnet.from_subnet_id(self, f"Subnet{i}", subnet_id)
                for i, subnet_id in enumerate(subnet_ids)
            ]
        )
