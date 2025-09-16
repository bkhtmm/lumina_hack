#  Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#  SPDX-License-Identifier: MIT-0

import boto3

print("Loading Detect Language...")
s3_client = boto3.client("s3")

def handler(e, context):
    """
    Simplified language detection - defaults to English
    Llama API works well with English, so we don't need complex language detection
    """
    event = e["event"]
    
    # Default to English since Llama API works best with English
    # and most business conversations are in English
    event["dominant_language_code"] = "en"
    event["dominant_language"] = "english"

    return {
        "event": event,
        "status": "SUCCEEDED",
    }
