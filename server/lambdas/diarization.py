#  Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#  SPDX-License-Identifier: MIT-0

import os
import boto3
import json
from lemonfox_client import LemonfoxClient

print("Loading Diarization Function...")
s3_client = boto3.client("s3")
lemonfox_client = LemonfoxClient()


def handler(e, context):
    event = e["event"]
    s3_bucket = event["bucket"]
    key = event["key"]
    output_key = event["output_s3_key"]
    content_type = event.get("content_type", "")
    
    try:
        # For MP3 files, use the original file path
        # For WAV files, use the converted WAV file path
        if content_type in ['mp3', 'audio/mp3']:
            audio_url = f"s3://{s3_bucket}/{key}"
        else:
            wav_file = event["audio_wav_file"]
            audio_url = f"s3://{s3_bucket}/{output_key}/{wav_file}"
        
        print(f"Starting Lemonfox API call for diarization of {audio_url}")
        print(f"Content type: {content_type}")
        
        # Call Lemonfox API for transcription with diarization
        result = lemonfox_client.transcribe_with_diarization(audio_url)
        
        # Process the result to extract diarization data
        diarization_data = lemonfox_client.process_lemonfox_result(result)
        
        # Save diarization data to S3
        diarization_file_suffix = "diarization.txt"
        diarization_file_path = f"/tmp/{diarization_file_suffix}"
        
        with open(diarization_file_path, "w") as f:
            f.write(diarization_data)
        
        diarization_s3_key = f"{output_key}/{diarization_file_suffix}"
        s3_client.upload_file(diarization_file_path, s3_bucket, diarization_s3_key)
        
        # Update event with diarization output path
        event["diarization_out_path"] = f"s3://{s3_bucket}/{diarization_s3_key}"
        event["lemonfox_result"] = result  # Store full result for transcription step
        event["diarization_file"] = diarization_file_suffix
        
        print(f"✅ Diarization completed for {key}")
        print(f"Diarization output: s3://{s3_bucket}/{diarization_s3_key}")
        
        return {"event": event, "status": "SUCCEEDED"}
        
    except Exception as e:
        print(f"❌ Error in diarization: {str(e)}")
        print(
            "Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as "
            "this function.".format(key, s3_bucket)
        )
        raise e
