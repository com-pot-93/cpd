from openai import OpenAI
import json
import os
from dotenv import dotenv_values

config = dotenv_values(".env")
open_key = config["OPENAI_API_KEY"]

""" get openai key from .env """
open_app = OpenAI(
  api_key = open_key,
  #api_key=os.environ.get("OPENAI_API_KEY"),
)

""" define prompt parametes """
def get_parameters():
    file = os.path.join(os.getcwd(),'round_trip', 'llm_connect','parameters.json')
    with open(file, "r") as infile:
        params = json.load(infile)
        return params

def set_parameter(key,value):
    params = get_parameters()
    params[key] = value
    file = os.path.join(os.getcwd(),'round_trip' ,'llm_connect','parameters.json')
    with open(file, 'w') as f:
        json.dump(params, f)

parameters = get_parameters()

""" call gpt model via completions """
def ask_gpt_complete(prompt,model,parameters):
    try:
        response = open_app.completions.create(
            model=model,
            prompt = prompt,
            max_tokens=parameters["max_tokens"],
            temperature = parameters["temperature"],
            top_p = parameters["top_p"],
            stop = ["ooooooooooo"]
            )
        return response.choices[0].text
    except Exception as e:
        return e

""" call gpt model via chat completions - only user """
def ask_gpt_chat(model,parameters,prompt):
    try:
        response = open_app.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=parameters["temperature"],
            max_tokens=parameters["max_tokens"],
            top_p=parameters["top_p"],
            frequency_penalty=parameters["frequency_penalty"],
            presence_penalty=parameters["presence_penalty"]
        )
        return response.choices[0].message.content
    except Exception as e:
        return e

""" call gpt model via chat completions - only user and system """
def ask_gpt_system(model,parameters,prompt,system_message):
    try:
        response = open_app.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": prompt},
                {"role": "system", "content": system_message}
            ],
            temperature=parameters["temperature"],
            max_tokens=parameters["max_tokens"],
            top_p=parameters["top_p"],
            frequency_penalty=parameters["frequency_penalty"],
            presence_penalty=parameters["presence_penalty"]
        )
        return response.choices[0].message.content
    except Exception as e:
        return e

""" call gpt model """
def ask_gpt(model,prompt,system_message=0):
    try:
        if "instruct" in model:
            response = ask_gpt_complete(prompt,model,parameters)
        else:
            if system_message == 0:
                response = ask_gpt_chat(model,parameters,prompt)
            else:
                response = ask_gpt_system(model,parameters,prompt,system_message)
        return response
    except Exception as e:
        return e

