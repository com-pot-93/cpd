import os, sys
import json
import logging
import argparse
import csv
import time
import pandas as pd
sys.path.append("./round_trip")
from round_trip.llm_connect.sap_hub_call import generate_with_timeout

system_prompt = """
You are an expert in BPMN (Business Process Model and Notation) modeling. Your task is to evaluate and interpret user-provided modifications to a BPMN process model.
Your responsibilities include:
    (a) Validating whether the provided modification contains sufficient and unambiguous information to be applied.
    (b) Mapping each modification to a predefined change pattern (see list below).
    (c) Deriving the actual meaning of the modification based on BPMN semantics and the intent of the change pattern.
    (d) Ensuring compliance with BPMN modeling rules and the structure of the existing process.
Final output have to contain only the actual meaning of the user input in natural language without ambiguity and without any additional information.  If there is not enough information to perform changes return "NA".

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
    print(user_prompts)

    file_name = "./identify/{}-evaluation.csv".format(llm)
    survey_sheet = pd.read_csv(file_name)
    llm_results = survey_sheet.iloc[:,1:]
    llmcolumns = list(llm_results.columns.values)
    print(llmcolumns)
    for p in llmcolumns:
        output = {"mapping":[],"epap":[],"user":[],"meaning":[]}
        # p - expected pattern
        print("-----------------------------------------")
        all_results = llm_results[p].to_list()
        for r in range(0,len(all_results)):
            mapping = False
            epap = False
            llm_meaning = False
            result = all_results[r]
            if isinstance(result, str):
                if result in llmcolumns:   #in rulebase
                    mapping = True
                    if p == result:        #mapped
                        epap = True
                    else:                  #mismapped
                        epap = False
                    myprompt = user_prompts[p][r]
                    llm_meaning = generate_with_timeout(llm, myprompt, system_prompt, 0, response_format=False)
                    #llm_meaning = "test"
            output["mapping"].append(mapping)
            output['epap'].append(epap)
            output['user'].append(user_prompts[p][r])
            output['meaning'].append(llm_meaning)
            time.sleep(0.5)

        print(output)
        data_out = pd.DataFrame.from_dict(output)
        data_out.to_csv("./derive/{}/{}-{}-evaluation.csv".format(llm,llm,p), encoding='utf-8')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process models and text with retries and timeout.")
    parser.add_argument('--llm', type=str, required=True, help='Select llm mode: gpt or gemini')

    args = parser.parse_args()
    llm = args.llm.lower()
    if llm == 'gpt' or llm == 'gemini' or llm=='mistral':
        main_pipeline(llm)
    else:
        print('Please check selected llm model (only gpt or gemini are acceptable)!!!')
