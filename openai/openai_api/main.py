import os
import requests
import json

from dotenv import load_dotenv

load_dotenv()

class OpenAI_API:

    def __init__(self, api_key = os.environ.get("OPENAI_API_KEY")):
        self._api_key = api_key
        self._base_url = "https://api.openai.com/v1"
        self._headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._api_key}"
        }



    def get_models(self) -> dict:
        """
        Get a list of available models from the OpenAI API.

        Returns:
            dict: A dictionary containing information about the available models.
        """
        url = self._base_url + "/models"
        response = requests.get(url, headers=self._headers)
        return json.dumps(response.json(), indent=2)



    def call_openai_api(prompt, api_key, model="gpt-4", temperature=0.7, max_tokens=150):
        """
        A function to interact with the OpenAI API using the requests library.
        
        Args:
            prompt (str): The input prompt for the model.
            api_key (str): Your OpenAI API key.
            model (str): The OpenAI model to use (default: "gpt-4").
            temperature (float): The creativity level of the model (default: 0.7).
            max_tokens (int): The maximum number of tokens to generate (default: 150).

        Returns:
            dict: The response from the OpenAI API.
        """
        url = "https://api.openai.com/v1/completions"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        data = {
            "model": model,
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        try:
            response = requests.post(url, headers=headers, data=json.dumps(data))
            response.raise_for_status()  # Check for HTTP errors
            return response.json()
        
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return None



if __name__ == "__main__":
    openai = OpenAI_API()
    models = openai.get_models()
    print(models)