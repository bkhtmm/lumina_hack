#  Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#  SPDX-License-Identifier: MIT-0

import json
import os
import time
import boto3
from llama_client import Llama4ScoutClient

print("Loading Summarization Fn...")
s3_client = boto3.client("s3")
ssm_client = boto3.client("ssm")

# Llama4Scout Configuration
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "256"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.1"))

SUCCESS = "SUCCESS"
FAILED = "FAILED"

# Initialize Llama4Scout client
llama_client = Llama4ScoutClient()

SSM_LLM_SUMMARIZATION_NAME = "ci_summarization_prompt"
SSM_LLM_ACTION_PROMPT = "ci_action_prompt"
SSM_LLM_TOPIC_PROMPT = "ci_topic_prompt"
SSM_LLM_PRODUCT_PROMPT = "ci_product_prompt"
SSM_LLM_RESOLVED_PROMPT = "ci_resolved_prompt"
SSM_LLM_CALLBACK_PROMPT = "ci_callback_prompt"
SSM_LLM_POLITE_PROMPT = "ci_politeness_prompt"
SSM_LLM_AGENT_SENTIMENT_PROMPT = "ci_agent_sentiment_prompt"
SSM_LLM_CUSTOMER_SENTIMENT_PROMPT = "ci_customer_sentiment_prompt"

def call_llama(parameters, prompt):
    """
    Call Llama4Scout API instead of Bedrock
    """
    return llama_client.generate_response(prompt, parameters)


def generate_llama_query(prompt, transcript, question=""):
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


def merge_json(original, addition):
    for k, v in addition.items():
        if k not in original:
            original[k] = v
        else:
            if isinstance(v, dict):
                merge_json(original[k], v)
            elif isinstance(v, list):
                for i in range(len(v)):
                    merge_json(original[k][i], v[i])
            else:
                if not original[k]:
                    original[k] = v


def handler(e, context):
    merge_json(e[0], e[1])
    merged_event = e[0]
    event = merged_event["event"]
    s3_bucket = event["bucket"]
    output_key = event["output_s3_key"]
    original_transcription_file = event["original_transcription_file"]
    language = event["dominant_language_code"]

    # Download original transcript file
    if language != 'original' and language != 'en':
        original_transcription_file = original_transcription_file.replace('original', 'translated')
        original_transcription_file = original_transcription_file.replace('en', 'translated')

    temp_transcription_file_path = "/tmp/" + original_transcription_file

    s3_client.download_file(
        s3_bucket,
        f"{output_key}/{original_transcription_file}",
        temp_transcription_file_path,
    )

    transcript_data = ""
    with open(temp_transcription_file_path, "rt") as file:
        for line in file.readlines():
            transcript_data += line.strip() + "\n"

    try:
        llm_summarization_prompt = ssm_client.get_parameter(
            Name=SSM_LLM_SUMMARIZATION_NAME
        )
        prompt = llm_summarization_prompt["Parameter"]["Value"]
        query_response = generate_llama_query(prompt, transcript_data, "")
        event["Summarization"] = query_response
        time.sleep(30)

        llm_action_prompt = ssm_client.get_parameter(
            Name=SSM_LLM_ACTION_PROMPT
        )
        prompt = llm_action_prompt["Parameter"]["Value"]
        query_response = generate_llama_query(prompt, transcript_data, "")
        event["ActionItems"] = query_response
        time.sleep(30)

        llm_topic_prompt = ssm_client.get_parameter(
            Name=SSM_LLM_TOPIC_PROMPT
        )
        prompt = llm_topic_prompt["Parameter"]["Value"]
        query_response = generate_llama_query(prompt, transcript_data, "")
        event["Topic"] = query_response
        time.sleep(30)

        llm_polite_prompt = ssm_client.get_parameter(
            Name=SSM_LLM_POLITE_PROMPT
        )
        prompt = llm_polite_prompt["Parameter"]["Value"]
        query_response = generate_llama_query(prompt, transcript_data, "")
        event["Politeness"] = query_response
        time.sleep(30)

        llm_callback_prompt = ssm_client.get_parameter(
            Name=SSM_LLM_CALLBACK_PROMPT
        )
        prompt = llm_callback_prompt["Parameter"]["Value"]
        query_response = generate_llama_query(prompt, transcript_data, "")
        event["Callback"] = query_response
        time.sleep(30)

        llm_product_prompt = ssm_client.get_parameter(
            Name=SSM_LLM_PRODUCT_PROMPT
        )
        prompt = llm_product_prompt["Parameter"]["Value"]
        query_response = generate_llama_query(prompt, transcript_data, "")
        event["Product"] = query_response
        time.sleep(30)

        llm_resolved_prompt = ssm_client.get_parameter(
            Name=SSM_LLM_RESOLVED_PROMPT
        )
        prompt = llm_resolved_prompt["Parameter"]["Value"]
        query_response = generate_llama_query(prompt, transcript_data, "")
        event["Resolution"] = query_response
        time.sleep(30)

        llm_agent_sentiment_prompt = ssm_client.get_parameter(
            Name=SSM_LLM_AGENT_SENTIMENT_PROMPT
        )
        prompt = llm_agent_sentiment_prompt["Parameter"]["Value"]
        query_response = generate_llama_query(prompt, transcript_data, "")
        event["AgentSentiment"] = str(query_response).split(',', 1)[0]
        time.sleep(30)

        llm_customer_sentiment_prompt = ssm_client.get_parameter(
            Name=SSM_LLM_CUSTOMER_SENTIMENT_PROMPT
        )
        prompt = llm_customer_sentiment_prompt["Parameter"]["Value"]
        query_response = generate_llama_query(prompt, transcript_data, "")
        event["CustomerSentiment"] = str(query_response).split(',', 1)[0]
        time.sleep(30)

        print(f"Summarization completed for {output_key}")
    except Exception as err:
        query_response = "An error occurred generating Llama4Scout query response."
        print(err)

    return {
        "event": event,
        "status": "SUCCEEDED",
    }
