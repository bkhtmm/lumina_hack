#  Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#  SPDX-License-Identifier: MIT-0

print("Checking if entities job is complete...")

def handler(e, context):
    """
    Simplified entities job status - always returns completed
    since Llama API handles entity detection directly
    """
    event = e["event"]
    
    # Since Llama API handles entities, we always return completed
    event['entities_job_status'] = True
    event['entities_job_output_file'] = "llama-api-entities-output"

    print(f"Entities Detection Job completed via Llama API!!")
    
    return {
        "event": event,
        "status": "SUCCEEDED",
    }
