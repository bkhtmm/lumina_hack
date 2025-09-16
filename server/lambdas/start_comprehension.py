#  Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#  SPDX-License-Identifier: MIT-0

import os
import json

print("Loading Start Comprehend Jobs...")

def handler(e, context):
    """
    Simplified handler - Comprehend functionality replaced by Llama API
    Llama API already handles sentiment analysis and entity detection
    """
    event = e["event"]
    
    # Since Llama API handles sentiment and entities, we just mark as completed
    event["sentiment_job_id"] = "llama-api-sentiment"
    event["entities_job_id"] = "llama-api-entities"
    
    return {
        "event": event,
        "status": "SUCCEEDED",
    }
