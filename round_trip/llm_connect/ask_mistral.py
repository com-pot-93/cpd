import concurrent.futures
import json
import logging
import os
import sys
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from functools import partial
#import dotenv
from dotenv import dotenv_values

from mistralai import Mistral
from ratelimit import limits, sleep_and_retry
import time

config = dotenv_values(".env")
API_KEY = config["MISTRAL_KEY"]
client = Mistral(api_key=API_KEY)

#mistral-large-latest
""" define prompt parametes """
def get_parameters():
    file = os.path.join(os.getcwd(),'round_trip', 'llm_connect','parameters.json')
    with open(file, "r") as infile:
        params = json.load(infile)
        return params

parameters = get_parameters()

@sleep_and_retry
@limits(calls=1, period=3)
def ask_mistral(model,user_prompt,system_prompt):
    try:
        chat_response = client.chat.complete(
            model= model,
            temperature=parameters["temperature"],
            max_tokens=parameters["max_tokens"],
            frequency_penalty = parameters["frequency_penalty"],
            presence_penalty = parameters["presence_penalty"],
            messages = [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ],stream=False
        )
        print("return")
        #print(chat_response)
    except:
        time.sleep(70)
        try:
            chat_response = client.chat.complete(
                model= model,
                temperature=parameters["temperature"],
                max_tokens=parameters["max_tokens"],
                frequency_penalty = parameters["frequency_penalty"],
                presence_penalty = parameters["presence_penalty"],
                messages = [
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': user_prompt}
                ],stream=False
            )
            print("again")
        except:
            time.sleep(70)
            chat_response = client.chat.complete(
                model= model,
                temperature=parameters["temperature"],
                max_tokens=parameters["max_tokens"],
                frequency_penalty = parameters["frequency_penalty"],
                presence_penalty = parameters["presence_penalty"],
                messages = [
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': user_prompt}
                ],stream=False
            )
            print("again again")

    return chat_response.choices[0].message.content





