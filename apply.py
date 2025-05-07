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
You are an expert in BPMN modeling, specifically in Mermaid.js format.
Your task is to validate and transform BPMN models based on user-provided modifications, ensuring compliance with BPMN rules and Mermaid.js syntax.
The Mermaid.js syntax for BPMN models is described as follows:
The graph must use the LR (Left to Right) direction.
Each mermaid js node must have the following structure:
id:type:shape and text
    id - it is a unique identifier. Id can be only an integer from 0 to n. Each node has a unique identifier
    type - defines the type of the element regarding to BPMN 2.0 notation.
        possible types are: start event, end event, task, subprocess, exclusive, inclusive and parallel gateway.
        Based on the type of the node following shapes and texts are to be used:
        startevent: ((startevent))      i.e., id:startevent:((startevent))
        endevent: (((endevent)))        i.e., id:endevent:(((endevent)))
        task: (task label)              i.e., id:task:(task label)
        subprocess: (subprocess label)  i.e., id:subprocess:(subprocess label)
        exclusivegateway: {x}           i.e., id:exclusivegateway:{x}
        parallelgateway: {AND}          i.e., id:parallelgateway:{AND}
        inclusivegateway: {O}           i.e., id:inclusivegateway:{O}

All gateways must have both a split and a merge point.
Each gateway that initiates a split must be properly closed by a merge gateway of the same type (e.g., an exclusive gateway must be merged by another exclusive gateway).

All nodes that have occurred more than once should have following structure: id:type: (i.e., 2:task: ) by futher occurrence.
It is strictly prohibited to use only id (i.e. 2) as a reference.

All elements are connected with each other with the help of the direction.
    direction: -->
If there are some conditions or annotations it is necessary to use text on links (i.e., edge labels)
    edge label: |condition or annotation|
Edge label is always located between 2 nodes: id:exclusivegateway:{x} --> |condition or annotation|id:task:(task label)

Return only mermaid.js as text without any additional information!
"""

def main_pipeline(llm):
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()]
    )
    logger = logging.getLogger("{}Logger".format(llm.upper()))

    directory = './derive/{}'.format(llm)  # set directory path

    for root, _, files in os.walk(directory):
        for filename in files:  # loop through files in the current directory
            file_name = os.path.join(root, filename)
            meaning_sheet = pd.read_csv(file_name)
            meaning_prompts = meaning_sheet.iloc[:,4:]
            meaning_prompts = meaning_prompts['meaning'].to_list()
            pattern = filename.split("-")[1]
            output_dir = './AAO/{}/{}'.format(llm,pattern)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            if pattern == "AP7":
                input_name = 'ipm-7'
            elif pattern == "AP15":
                input_name = "ipm-15"
            elif pattern == "AP16":
                input_name = "ipm-16"
            elif pattern == "AP17" or pattern == "AP18":
                input_name = "ipm-17"
            else:
                input_name = "ipm-1"
            inputfile = "./input/{}.txt".format(input_name)
            mermaid = open(inputfile, "r")
            bpmn = mermaid.read()
            for m in range(0,len(meaning_prompts)):
                meaning = meaning_prompts[m]
                if isinstance(meaning, str):
                    if meaning != "NA":
                        user_prompt = "Consider following process model: {}\n Apply these changes to the model: {}".format(bpmn,meaning)
                        llm_response = generate_with_timeout(llm, user_prompt, system_prompt, 0, response_format=False)
                        with open("{}/{}.txt".format(output_dir,m), "w") as out:
                            out.write(llm_response)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process models and text with retries and timeout.")
    parser.add_argument('--llm', type=str, required=True, help='Select llm mode: gpt or gemini')

    args = parser.parse_args()
    llm = args.llm.lower()
    if llm == 'gpt' or llm == 'gemini' or llm=='mistral':
        main_pipeline(llm)
    else:
        print('Please check selected llm model (only gpt or gemini are acceptable)!!!')
