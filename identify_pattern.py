import os, sys
import json
import logging
import argparse
import csv
import time
import pandas as pd
sys.path.append("./round_trip")
from round_trip.llm_connect.ask_open_ai import ask_gpt
from round_trip.llm_connect.ask_gemini import ask_gemini
from round_trip.llm_connect.ask_mistral import ask_mistral

#prompt :
system_prompt = """
You are an expert in BPMN (Business Process Model and Notation) modeling. Your task is to evaluate and interpret user-provided modifications to a BPMN process model.
Your task is to classify the user input into one of the predefined change patterns for process model redesign, if a matching pattern exists.
Use the following classification of change patterns to interpret user modifications:
{
"AP1":"Insert Process Fragment. Adds a new process fragments between two directly succeeding activities",
"AP2":"Delete Process Fragment. Removes an existing process fragment and consequently flatten the hierarchy if necessary",
"AP3":"Move Process Fragment. Shifts an existing process fragment from its current position to a new one",
"AP4":"Replace Process Fragment. Replaces Process Fragment & replace an existing process fragment with by a new one",
"AP5":"Swap Process Fragments. Swaps an existing process fragment with another existing process fragment",
"AP8.1":"Embed Process Fragment in Pre-Conditional Loop. An existing process fragment is embedded in a loop to allow for a repeated execution between 0 and N times",
"AP8.2":"Embed Process Fragment in Post-Conditional Loop. An existing process fragment is embedded in a loop to allow for a repeated execution between 1 and N times",
"AP9":"Parallelize Process Fragments. Parallelization of existing process fragments which were confined to be executed in sequence",
"AP10":"Embed Process Fragment in Conditional Branch. An existing process fragment is embedded in a conditional branch",
"AP14":"Copy Process Fragment. Copies an existing process fragment and paste it to a new position",
"AP6":"Extract Sub Process. Extracts an existing process fragment to encapsulate it in a separate sub process",
"AP7":"Inline Sub Process. Inlines a sub process into the parent process, and consequently flatten the hierarchy of the overall process",
"AP13":"Update Condition. Updates transition conditions in a process",
"AP19":"Replace Gateways. Replaces existing gateways (both splitting and merging) in specified fragment simultaneously with the gateways of the other type",
"AP15":"Split Process Fragment. Splits an existing process fragment into a sequence of multiple separate new process fragments",
"AP16":"Merge Process Fragment. Merges multiple existing separate process fragments into one new process fragment",
"AP17":"Delete Entire Branch. Removes single entire branch inside selected gateways and consequently flatten the hierarchy if necessary",
"AP18":"Leave Single Branch. Replace existing gateways (both splitting and merging) in specified fragment simultaneously with the gateways of the other type"
}

If a match is found, return only the pattern ID. Only one pattern can be matched.
If no match is found, return NA. No other information is allowed to be returned!!!
"""

def main_pipeline(llm):
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()]
    )
    logger = logging.getLogger("{}Logger".format(llm.upper()))

    #open excel file
    file_name = "./survey.xlsx"
    survey_sheet = pd.read_excel(file_name)
    user_prompts = survey_sheet.iloc[:,6:24]
    mycolumns = list(user_prompts.columns.values)

    output = {}

    for p in mycolumns:
        # p - expected pattern
        print("-----------------------------------------")
        all_prompts = user_prompts[p].to_list()
        output[p] = []
        for user_prompt in all_prompts:
            # if prompt is float - ignore
            if isinstance(user_prompt, str):
                if llm == "gemini":
                    llm_pattern = ask_gemini("gemini-2.5-flash",user_prompt,system_prompt)
                elif llm == "gpt":
                    llm_pattern = ask_gpt("gpt-4o",user_prompt,system_prompt)
                elif llm == "mistral":
                    llm_pattern = ask_mistral("mistral-large-2411",user_prompt,system_prompt)
                    #llm_pattern = ask_mistral("mistral-large-2411",user_prompt,system_prompt)
                #llm_pattern = generate_with_timeout(llm, user_prompt, system_prompt, 0, response_format=False)
                output[p].append(llm_pattern)
        print(output)

    print(output)
    data_out = pd.DataFrame.from_dict(output)
    data_out.to_csv("./identify/{}-evaluation.csv".format(llm), encoding='utf-8')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process models and text with retries and timeout.")
    parser.add_argument('--llm', type=str, required=True, help='Select llm mode: gpt or gemini')

    args = parser.parse_args()
    llm = args.llm.lower()
    if llm == 'gpt' or llm == 'gemini' or llm=='mistral':
        main_pipeline(llm)
    else:
        print('Please check selected llm model (only gpt or gemini are acceptable)!!!')
