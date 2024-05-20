import requests
import time
import os
import urllib.parse
from dotenv import load_dotenv


class GroqChatClient:

    def __init__(
        self,
        api_key=os.environ["GROQ_API_KEY"],
        model="mixtral-8x7b-32768",
        sleep_time=5,
    ):
        load_dotenv()
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.sleep_time = sleep_time

    def send_chat_message(self, content, stop_if_error=False):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        if len(content) > 32768:
            print(f"""Dividing the content into chunks... {len(content)} characters""")
            content_chunks = content.split("Title:")

            prompt = content_chunks[0]

            size_prompt = len(content_chunks) // 2

            # add at the beginning of every chunk the string "Title:"
            for i in range(1, len(content_chunks)):
                content_chunks[i] = "Title:" + content_chunks[i]

            summary_half = self.send_chat_message(
                prompt + self.concat_list_elements(content_chunks[1 : size_prompt + 1])
            )
            time.sleep(self.sleep_time)
            summary_second_half = self.send_chat_message(
                prompt + self.concat_list_elements(content_chunks[size_prompt + 1 :])
            )

            print(f"""  Summary_half... {len(summary_half)} characters""")
            print(f"""  Summary_second_half... {len(summary_half)} characters""")

            return self.send_chat_message(prompt + summary_half + summary_second_half)

        data = {
            "messages": [
                {"role": "user", "content": self.handle_breaker_chars(content)}
            ],
            "model": self.model,
        }

        time.sleep(self.sleep_time)

        try:
            #   print("Calling Groq API...")
            response = requests.post(self.base_url, headers=headers, json=data)
            response.raise_for_status()
            response_data = response.json()

            # Extract the "content" part from the response
            if "choices" in response_data and len(response_data["choices"]) > 0:
                assistant_message = response_data["choices"][0]["message"]
                return assistant_message.get("content", None)
            else:
                return None
        except requests.exceptions.HTTPError as e:
            print(f"Error sending chat message: {e}")

            if e.response.status_code == 429:
                print("Rate limit exceeded. Waiting for 1 minutes...")
                time.sleep(60)
                return self.send_chat_message(content, stop_if_error)

            if stop_if_error:
                return ""

            time.sleep(self.sleep_time + 2)
            return self.send_chat_message(content, True)

    def handle_breaker_chars(self, string):
        """
        Escapes potential breaker characters in a string for HTTP request body.

        Args:
            string: The string to be sanitized.

        Returns:
            The sanitized string with escaped breaker characters.
        """
        # Escape characters that might break the HTTP request body
        escaped_string = urllib.parse.quote(string, safe="")
        return escaped_string

    def concat_list_elements(self, arr):
        return " ".join([str(elem) for elem in arr])
