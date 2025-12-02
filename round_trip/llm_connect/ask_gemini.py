from google import genai
from google.genai import types
import json
import os
from dotenv import dotenv_values

config = dotenv_values(".env")
gemini_key = config["GEMINI_API_KEY"]

client = genai.Client(api_key=gemini_key)

""" define prompt parametes """
def get_parameters():
    file = os.path.join(os.getcwd(),'round_trip', 'llm_connect','parameters.json')
    with open(file, "r") as infile:
        params = json.load(infile)
        return params

parameters = get_parameters()

def ask_gemini(model,user_prompt,system_prompt):
    try:
        response = client.models.generate_content(
            model=model,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                maxOutputTokens = parameters["max_tokens"],
                topP=parameters["top_p"],
                frequencyPenalty = parameters["frequency_penalty"],
                temperature=parameters["temperature"],
                automatic_function_calling=types.AutomaticFunctionCallingConfig(
                    disable=True
                ),
                ),
            contents=user_prompt
        )
        print(response)
        return response.text
    except Exception as e:
        return e




