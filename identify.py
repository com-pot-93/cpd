import os, sys
import json
import logging
import argparse
import csv
import time
import pandas as pd
sys.path.append("./round_trip")
from round_trip.llm_connect.sap_hub_call import generate_with_timeout

#prompt :
system_prompt = """
Consider following predefined change patterns for business process model redesign:
{
"AP1":"Insert Process Fragment",
"AP2":"Delete Process Fragment",
"AP3":"Move Process Fragment",
"AP4":"Replace Process Fragment",
"AP5":"Swap Process Fragments",
"AP8.1":"Embed Process Fragment in Pre-Conditional Loop",
"AP8.2":"Embed Process Fragment in Post-Conditional Loop",
"AP9":"Parallelize Process Fragments",
"AP10":"Embed Process Fragment in Conditional Branch",
"AP14":"Copy Process Fragment",
"AP6":"Extract Sub Process",
"AP7":"Inline Sub Process",
"AP13":"Update Condition",
"AP19":"Replace Gateways",
"AP15":"Split Process Fragment",
"AP16":"Merge Process Fragment",
"AP17":"Delete Entire Branch",
"AP18":"Leave Single Branch"
}.

Classify the user input into one of the predefined change patterns, if a matching pattern exists.
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
    user_prompts = survey_sheet.iloc[:,5:23]
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
                llm_pattern = generate_with_timeout(llm, user_prompt, system_prompt, 0, response_format=False)
                output[p].append(llm_pattern)
                time.sleep(0.5)

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
