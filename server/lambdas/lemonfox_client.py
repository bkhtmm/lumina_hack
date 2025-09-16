#  Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#  SPDX-License-Identifier: MIT-0

import requests
import time
import os
import cfg

class LemonfoxClient:
    """
    Client for Lemonfox.ai API - handles transcription and speaker diarization
    """
    
    def __init__(self):
        self.api_key = cfg.LEMONFOX_API_KEY
        self.base_url = cfg.LEMONFOX_BASE_URL
        self.timeout = cfg.LEMONFOX_TIMEOUT
        self.max_retries = cfg.LEMONFOX_MAX_RETRIES
        self.min_speakers = cfg.LEMONFOX_MIN_SPEAKERS
        self.max_speakers = cfg.LEMONFOX_MAX_SPEAKERS
        self.headers = {"Authorization": f"Bearer {self.api_key}"}
    
    def transcribe_with_diarization(self, audio_url, language="english"):
        """
        Transcribe audio with speaker diarization using Lemonfox API
        
        Args:
            audio_url (str): URL or S3 path to the audio file
            language (str): Language of the audio (default: "english")
            
        Returns:
            dict: Lemonfox API response with transcription and speaker segments
        """
        url = f"{self.base_url}/audio/transcriptions"
        
        data = {
            "file": audio_url,
            "response_format": "verbose_json",
            "speaker_labels": True,
            "min_speakers": self.min_speakers,
            "max_speakers": self.max_speakers,
            "language": language
        }
        
        print(f"Calling Lemonfox API for transcription with diarization...")
        print(f"Audio URL: {audio_url}")
        print(f"Language: {language}")
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    url, 
                    headers=self.headers, 
                    data=data, 
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                result = response.json()
                print(f"✅ Lemonfox API call successful on attempt {attempt + 1}")
                return result
                
            except requests.exceptions.Timeout:
                print(f"⚠️ Attempt {attempt + 1}/{self.max_retries}: Lemonfox API request timed out.")
            except requests.exceptions.RequestException as e:
                print(f"⚠️ Attempt {attempt + 1}/{self.max_retries}: Lemonfox API request failed: {e}")
            except Exception as e:
                print(f"⚠️ Attempt {attempt + 1}/{self.max_retries}: Unexpected error: {e}")
            
            if attempt < self.max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"⏳ Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
        
        raise Exception(f"❌ Failed to get response from Lemonfox API after {self.max_retries} attempts.")
    
    def transcribe_only(self, audio_url, language="english"):
        """
        Transcribe audio without speaker diarization
        
        Args:
            audio_url (str): URL or S3 path to the audio file
            language (str): Language of the audio (default: "english")
            
        Returns:
            dict: Lemonfox API response with transcription only
        """
        url = f"{self.base_url}/audio/transcriptions"
        
        data = {
            "file": audio_url,
            "response_format": "verbose_json",
            "speaker_labels": False,
            "language": language
        }
        
        print(f"Calling Lemonfox API for transcription only...")
        print(f"Audio URL: {audio_url}")
        print(f"Language: {language}")
        
        try:
            response = requests.post(url, headers=self.headers, data=data, timeout=self.timeout)
            response.raise_for_status()
            
            result = response.json()
            print(f"✅ Lemonfox API call successful")
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Lemonfox API request failed: {e}")
            raise Exception(f"Failed to transcribe audio: {e}")
    
    def translate_and_transcribe(self, audio_url, language="english"):
        """
        Translate audio to English and transcribe
        
        Args:
            audio_url (str): URL or S3 path to the audio file
            language (str): Source language of the audio (default: "english")
            
        Returns:
            dict: Lemonfox API response with translation and transcription
        """
        url = f"{self.base_url}/audio/transcriptions"
        
        data = {
            "file": audio_url,
            "response_format": "verbose_json",
            "speaker_labels": True,
            "min_speakers": self.min_speakers,
            "max_speakers": self.max_speakers,
            "language": language,
            "translate": True
        }
        
        print(f"Calling Lemonfox API for translation and transcription...")
        print(f"Audio URL: {audio_url}")
        print(f"Source Language: {language}")
        
        try:
            response = requests.post(url, headers=self.headers, data=data, timeout=self.timeout)
            response.raise_for_status()
            
            result = response.json()
            print(f"✅ Lemonfox API call successful")
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Lemonfox API request failed: {e}")
            raise Exception(f"Failed to translate and transcribe audio: {e}")
    
    def process_lemonfox_result(self, result):
        """
        Process Lemonfox result to extract diarization data in expected format
        
        Args:
            result (dict): Lemonfox API response
            
        Returns:
            str: Diarization data in format expected by chunking.py
        """
        diarization_lines = []
        
        if "segments" not in result:
            print("⚠️ No segments found in Lemonfox result")
            return ""
        
        for segment in result["segments"]:
            start_time = segment.get("start", 0)
            end_time = segment.get("end", 0)
            speaker = segment.get("speaker", "SPEAKER_00")
            
            # Convert to the format expected by chunking.py
            line = f"{self._format_time(start_time)} --> {self._format_time(end_time)} {speaker}"
            diarization_lines.append(line)
        
        diarization_data = "\n".join(diarization_lines)
        print(f"✅ Processed {len(diarization_lines)} diarization segments")
        return diarization_data
    
    def _format_time(self, seconds):
        """
        Convert seconds to HH:MM:SS.mmm format
        
        Args:
            seconds (float): Time in seconds
            
        Returns:
            str: Formatted time string
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"
    
    def get_transcription_text(self, result, language="original"):
        """
        Extract transcription text from Lemonfox result
        
        Args:
            result (dict): Lemonfox API response
            language (str): Language preference ("original" or "en" for original, else translated)
            
        Returns:
            str: Transcription text
        """
        if language == "original" or language == "en":
            # Use original language transcription
            text = result.get("text", "")
            print(f"✅ Extracted original language transcription ({len(text)} characters)")
            return text
        else:
            # Use translation if available
            translated_text = result.get("translated_text", "")
            if translated_text:
                print(f"✅ Extracted translated transcription ({len(translated_text)} characters)")
                return translated_text
            else:
                # Fallback to original text
                text = result.get("text", "")
                print(f"⚠️ No translation available, using original text ({len(text)} characters)")
                return text
