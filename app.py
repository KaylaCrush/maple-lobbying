#!/usr/bin/env python3
import os

import aws_cdk as cdk

from src.cdk import CiCdStack


app = cdk.App()
CiCdStack(
    app,
    "Maple",
    # maple@alexjball.com
    env=cdk.Environment(account="968366361019", region="us-east-1"),
)

app.synth()
