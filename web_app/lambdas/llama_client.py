#  Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#  SPDX-License-Identifier: MIT-0

import requests
import json
import os
import time

class Llama4ScoutClient:
    """
    Client for Llama4Scout API integration
    Replaces Amazon Bedrock for LLM operations
    """
    
    def __init__(self):
        self.api_endpoint = "https://bkwg3037dnb7aq-8000.proxy.runpod.net/v1/chat/completions"
        self.model_name = "llama4scout"
        self.max_tokens = int(os.getenv("MAX_TOKENS", "1024"))
        self.temperature = float(os.getenv("TEMPERATURE", "0.1"))
        self.timeout = int(os.getenv("API_TIMEOUT", "30"))
        self.max_retries = int(os.getenv("MAX_RETRIES", "3"))
    
    def generate_response(self, prompt, parameters=None):
        """
        Generate response using Llama4Scout API
        
        Args:
            prompt (str): The input prompt
            parameters (dict): Optional parameters like max_tokens, temperature
            
        Returns:
            str: Generated response text
        """
        if parameters is None:
            parameters = {}
        
        payload = {
            "model": self.model_name,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": parameters.get("max_tokens", self.max_tokens),
            "temperature": parameters.get("temperature", self.temperature)
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        # Retry logic with exponential backoff
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    self.api_endpoint,
                    headers=headers,
                    json=payload,
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                result = response.json()
                
                # Extract the generated text from response
                if "choices" in result and len(result["choices"]) > 0:
                    content = result["choices"][0]["message"]["content"]
                    return content.strip()
                else:
                    print(f"No choices in API response: {result}")
                    return "Error: No response generated"
                    
            except requests.exceptions.Timeout:
                print(f"API request timeout (attempt {attempt + 1}/{self.max_retries})")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                else:
                    return "Error: API request timeout"
                    
            except requests.exceptions.RequestException as e:
                print(f"API request failed (attempt {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                else:
                    return f"Error: API request failed - {str(e)}"
                    
            except (KeyError, IndexError, json.JSONDecodeError) as e:
                print(f"Response parsing failed: {e}")
                return f"Error: Invalid response format - {str(e)}"
                
        return "Error: All retry attempts failed"
    
    def test_connection(self):
        """
        Test the API connection with a simple request
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        test_prompt = "Hello, can you respond with just the word TEST?"
        response = self.generate_response(test_prompt, {"max_tokens": 10})
        return "TEST" in response.upper()
