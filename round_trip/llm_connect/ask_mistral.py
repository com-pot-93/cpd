import concurrent.futures
import json
import logging
import os
import sys
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from functools import partial
import dotenv
from mistralai import Mistral
from ratelimit import limits, sleep_and_retry
import time

config = dotenv_values(".env")
API_KEY = config["MISTRAL_KEY"]
client = Mistral(api_key=API_KEY)

@sleep_and_retry
@limits(calls=1, period=3)
def generate_mistral(user_prompt,temperature,response_format=False):
    print("call")
    chat_response = client.chat.complete(
        model= "mistral-large-latest",
        temperature=temperature,
        max_tokens=4000,
        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ]
    )
    print("return")
    return chat_response.choices[0].message.content
    



