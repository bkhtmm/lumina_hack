#!/usr/bin/env python3

#  Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#  SPDX-License-Identifier: MIT-0

import aws_cdk as cdk
from constructs import Construct

# Remove ML stack import - no longer needed
# from ml_stack.cdk.ml_stack import MLStack
from server.cdk.server_stack import ServerStack
from web_app.cdk.app_stack import WebAppStack


class CIStack(Construct):
    def __init__(self, scope: Construct, id: str, *, prod=False):
        super().__init__(scope, id)

        # Server Stack (no longer depends on ML stack)
        server_stack = ServerStack(app, "ci-process")

        # UI Stack
        web_stack = WebAppStack(app, "ci-web")
        web_stack.add_dependency(server_stack)

        cdk.Tags.of(scope).add("App", "Conversation Intelligence")


app = cdk.App()
CIStack(app, "prod", prod=True)
app.synth()
