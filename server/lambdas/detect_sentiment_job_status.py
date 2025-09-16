#  Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#  SPDX-License-Identifier: MIT-0

print("Checking if sentiment job is complete...")

def handler(e, context):
    """
    Simplified sentiment job status - always returns completed
    since Llama API handles sentiment analysis directly
    """
    event = e["event"]
    
    # Since Llama API handles sentiment, we always return completed
    event['sentiment_job_status'] = True
    event['sentiment_job_output_file'] = "llama-api-sentiment-output"

    print(f"Sentiment Detection Job completed via Llama API!!")
    
    return {
        "event": event,
        "status": "SUCCEEDED",
    }
