#!/usr/bin/env python3
import json
import os

import aws_cdk as cdk

from backend_lambda_stack import BackendLambdaStack


app = cdk.App()

stage = app.node.try_get_context("stage") or "staging"
image_tag = app.node.try_get_context("image_tag")
if not image_tag:
    raise ValueError("Missing required CDK context: image_tag")

env = cdk.Environment(
    account=app.node.try_get_context("account"),
    region=app.node.try_get_context("region") or "us-east-1",
)

runtime_env_file = app.node.try_get_context("runtime_env_file")
runtime_env = {}
if runtime_env_file:
    with open(runtime_env_file, "r", encoding="utf-8") as f:
        loaded = json.load(f)
    runtime_env = {str(k): str(v) for k, v in loaded.items()}

openai_api_key = os.environ.get("OPENAI_API_KEY")
if openai_api_key:
    runtime_env["OPENAI_API_KEY"] = openai_api_key

if stage == "prod":
    BackendLambdaStack(
        app,
        "RengloProdStack",
        stage_name="prod",
        image_tag=image_tag,
        runtime_env=runtime_env,
        env=env,
    )
else:
    BackendLambdaStack(
        app,
        "RengloStagingStack",
        stage_name="staging",
        image_tag=image_tag,
        runtime_env=runtime_env,
        env=env,
    )

app.synth()
