#!/usr/bin/env python3

import os

from aws_cdk import App, Environment

from infrastructure.aws.cdk.application import AuditAPIStack

app = App()

AuditAPIStack(
    app,
    "AuditAPIStack",
    env=Environment(
        account=os.getenv("CDK_DEFAULT_ACCOUNT"),
        region=os.getenv("CDK_DEFAULT_REGION"),
    ),
)

app.synth()
