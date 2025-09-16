#  Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#  SPDX-License-Identifier: MIT-0

import json
import os

import boto3
from llama_client import Llama4ScoutClient

print("Loading Gen AI Query Fn...")
s3_client = boto3.client("s3")
ssm_client = boto3.client("ssm")
tableName = os.environ["UploadsTable"]
table = boto3.resource("dynamodb").Table(tableName)
s3_resource = boto3.resource("s3")

# Llama4Scout Configuration
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "1024"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.1"))

SUCCESS = "SUCCESS"
FAILED = "FAILED"
SSM_LLM_CHATBOT_NAME = "ci_chatbot_prompt"

# Initialize Llama4Scout client
llama_client = Llama4ScoutClient()


def call_llama(parameters, prompt):
    """
    Call Llama4Scout API instead of Bedrock
    """
    return llama_client.generate_response(prompt, parameters)


def generate_llama_query(prompt, transcript, question):
    """
    Generate query using Llama4Scout instead of Bedrock
    """
    # Clean up prompt formatting
    prompt = prompt.replace("<br>", "\n")
    prompt = prompt.replace("{transcript}", transcript)
    if question != "":
        prompt = prompt.replace("{question}", question)
    
    parameters = {
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS
    }
    
    generated_text = call_llama(parameters, prompt)
    return generated_text


def get_response():
    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
        },
    }


def get_err_response():
    return {
        "statusCode": 500,
        "headers": {
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
        },
    }


def handler(event, context):
    key = event["path"].replace("/genai/", "")
    request = json.loads(event["body"])
    payload = get_response()
    query_response = ""
    try:
        object_from_table = table.get_item(
            Key={"objectKey": "input/" + key},
            ConsistentRead=True,
        )
        if "Item" in object_from_table.keys():
            item = object_from_table["Item"]
            s3_bucket = item["bucketName"]
            output_key = item["outputFile"]
            s3_obj = s3_client.get_object(Bucket=s3_bucket, Key=output_key)
            s3_data = s3_obj["Body"].read().decode("utf-8")
            s3_client_data = json.loads(s3_data)
            if "TranslatedTranscript" in s3_client_data:
                transcript_data = s3_client_data["TranslatedTranscript"]
            else:
                transcript_data = s3_client_data["RawTranscript"]
            transcript_data = "".join(transcript_data)
            llm_summarization_prompt = ssm_client.get_parameter(
                Name=SSM_LLM_CHATBOT_NAME
            )
            prompt = llm_summarization_prompt["Parameter"]["Value"]
            query_response = generate_llama_query(prompt, transcript_data, request["query"])
            print(f"Got response from Llama4Scout for {key}")
    except Exception as err:
        query_response = "An error occurred generating Llama4Scout query response."
        print(query_response)
        print(err)
        return get_err_response()

    payload["body"] = query_response
    return payload
