#  Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#  SPDX-License-Identifier: MIT-0

import json
import os
import boto3
from lemonfox_client import LemonfoxClient

print("Loading Transcription Function...")
s3_client = boto3.client("s3")
lemonfox_client = LemonfoxClient()


def handler(e, context):
    event = e["event"]
    s3_bucket = event["bucket"]
    key = event["key"]
    output_key = event["output_s3_key"]
    language = event["dominant_language_code"]

    try:
        # Check if we already have Lemonfox result from diarization step
        if "lemonfox_result" in event:
            print("Using Lemonfox result from diarization step")
            result = event["lemonfox_result"]
        else:
            # Fallback: call Lemonfox API directly
            audio_url = f"s3://{s3_bucket}/{output_key}/{event['audio_wav_file']}"
            print(f"Calling Lemonfox API directly for transcription of {audio_url}")
            
            # Determine if we need translation
            if language == "original" or language == "en":
                result = lemonfox_client.transcribe_with_diarization(audio_url)
            else:
                result = lemonfox_client.translate_and_transcribe(audio_url, language)
        
        # Process the result to create transcription files
        transcription_data = lemonfox_client.get_transcription_text(result, language)
        
        # Save transcription data to S3
        transcription_file_suffix = "transcription.txt"
        transcription_file_path = f"/tmp/{transcription_file_suffix}"
        
        with open(transcription_file_path, "w") as f:
            f.write(transcription_data)
        
        transcription_s3_key = f"{output_key}/{transcription_file_suffix}"
        s3_client.upload_file(transcription_file_path, s3_bucket, transcription_s3_key)
        
        # Update event
        event["transcription_output"] = f"s3://{s3_bucket}/{transcription_s3_key}"
        event["transcription_complete"] = True
        
        print(f"✅ Transcription completed for {key}")
        print(f"Transcription output: s3://{s3_bucket}/{transcription_s3_key}")
        print(f"Transcription length: {len(transcription_data)} characters")
        
        return {"event": event, "status": "SUCCEEDED"}
        
    except Exception as e:
        print(f"❌ Error in transcription: {str(e)}")
        print(
            "Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as "
            "this function.".format(key, s3_bucket)
        )
        raise e
