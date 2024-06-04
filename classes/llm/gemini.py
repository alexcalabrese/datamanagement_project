import os
import requests
import random
import json
from typing import List, Dict, Any


class Gemini:
    def __init__(self):
        self.api_key = os.environ["GROQ_API_KEY"]

    def generate_content(self, prompt: str) -> Dict[str, Any]:
        """
        Generates content using the generative language API.

        Parameters
        ----------
        prompt (str): The text to use as a prompt for the content generation.

        Returns
        -------
        response_json (Dict[str, Any]): The JSON response from the API containing the generated content.
        """
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={}".format(
            self.api_key
        )

        headers = {"Content-Type": "application/json"}
        data = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0},
        }

        # add a try except block to catch any errors and check if the response is 200
        try:
            response = requests.post(url, headers=headers, json=data)
            response_json = response.json()
            return response_json
        except:
            print("Error with the request")
            return None

    def get_text_from_response(self, response_dict: dict) -> List[str]:
        """
        Extracts the generated text from the JSON response of the generative language API.

        Parameters
        ----------
        response_dict (dict): The JSON response as a dict.

        Returns
        -------
        texts (List[str]): A list of generated texts from the response.
        """
        # cover the case where the dict is None or empty
        if not response_dict:
            return [""]

        candidates = response_dict.get("candidates", [])

        # Initialize an empty list to store the texts
        texts = []

        for candidate in candidates:

            content = candidate.get("content", {})

            parts = content.get("parts", [])
            # Get the first part from the list (assuming there is only one part)
            part = parts[0] if parts else {}

            text = part.get("text", "")
            texts.append(text)

        if not texts:
            return [""]
        # Return the list of texts
        return texts
