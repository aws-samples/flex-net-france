#!/usr/bin/env python3

from aws_cdk import core

from vpc_peering_lab import VpcPeeringLabStack

props = { 'namespace': 'VPCPeeringLab' } 
app = core.App()

stack = VpcPeeringLabStack(app, "VPCPeeringLab-stack", props, env=core.Environment(account=app.node.try_get_context("AWS_account"), region=app.node.try_get_context("region")) )

app.synth()
