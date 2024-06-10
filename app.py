#!/usr/bin/env python3
import os
import yaml
import aws_cdk as cdk
from aws_cdk import Aspects
from cdk_nag import AwsSolutionsChecks

from SCP_Management_Pipeline.SCP_Management_Pipeline import SCPManagementPipeline

with open("./config.yaml") as stream:
    config = yaml.safe_load(stream)

app = cdk.App()
SCPManagementPipeline(app, "SCPManagementPipeline", config)

Aspects.of(app).add(AwsSolutionsChecks(verbose=False))

app.synth()
