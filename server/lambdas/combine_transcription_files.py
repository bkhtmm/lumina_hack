#  Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#  SPDX-License-Identifier: MIT-0

import json
import os
import boto3

print("Loading Combine Transcription Function...")
s3_client = boto3.client("s3")


def handler(e, context):
    event = e["event"]
    s3_bucket = event["bucket"]
    key = event["key"]
    output_key = event["output_s3_key"]
    language = event["dominant_language_code"]
    
    try:
        # Since we now have the full transcription from Lemonfox,
        # we just need to copy it to the final location
        
        transcription_key = f"{output_key}/transcription.txt"
        
        # Determine final file name based on language
        if language == "original" or language == "en":
            final_transcription_key = f"{output_key}/original_transcription.txt"
        else:
            final_transcription_key = f"{output_key}/translated_transcription.txt"
        
        # Copy transcription to final location
        copy_source = {"Bucket": s3_bucket, "Key": transcription_key}
        s3_client.copy_object(
            CopySource=copy_source,
            Bucket=s3_bucket,
            Key=final_transcription_key
        )
        
        # Update event
        event["original_transcription_file"] = f"s3://{s3_bucket}/{final_transcription_key}"
        
        print(f"✅ Transcription combined for {key}")
        print(f"Final transcription: s3://{s3_bucket}/{final_transcription_key}")
        
        return {"event": event, "status": "SUCCEEDED"}
        
    except Exception as e:
        print(f"❌ Error combining transcription: {str(e)}")
        print(
            "Error getting object {}. Make sure they exist and your bucket is in the same region as "
            "this function.".format(key)
        )
        raise e
