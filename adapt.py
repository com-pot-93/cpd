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
You are an expert in BPMN modeling, specifically in Mermaid.js format.
Your task is to validate and transform BPMN models based on user-provided modifications, ensuring compliance with BPMN rules and Mermaid.js syntax.
You are allowed to adjust only those parts of the process model mentioned in the user-provided modification. Other parts of the model have to stay unchanged.
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

Return only mermaid.js as text without any additional information! Give me just the raw Mermaid.js code without markdown formatting.
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
    error_list = []
    file_name = "./survey.xlsx"
    survey_sheet = pd.read_excel(file_name)
    user_inputs = survey_sheet.iloc[:,6:9]
    #user_inputs = survey_sheet.iloc[:,8:24]
    mycolumns = list(user_inputs.columns.values)
    print(mycolumns)

    for p in mycolumns: # p - expected pattern
        output_dir = './baseline/{}/{}'.format(llm,p)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        print(p,"-----------------------------------------")

        # get input model:
        if p == "AP7":
            input_name = 'ipm-7'
        elif p == "AP15":
            input_name = "ipm-15"
        elif p == "AP16":
            input_name = "ipm-16"
        elif p == "AP17" or p == "AP18":
            input_name = "ipm-17"
        else:
            input_name = "ipm-1"
        inputfile = "./input/{}.txt".format(input_name)
        mermaid = open(inputfile, "r")
        bpmn = mermaid.read()

        all_inputs = user_inputs[p].to_list()
        for u in range(0,len(all_inputs)):
            if os.path.exists("{}/{}.txt".format(output_dir,u)):
                print(u,".txt file : model was already generated")
            else:
                user_input = all_inputs[u]
                # if prompt is float - ignore
                if isinstance(user_input, str):
                    user_prompt = "Consider following process model: {}\n Apply these changes to the model: {}".format(bpmn,user_input)
                    if llm == "gemini":
                        llm_response = ask_gemini("gemini-2.5-flash",user_prompt,system_prompt)
                    elif llm == "gpt":
                        llm_response = ask_gpt("gpt-4o",user_prompt,system_prompt)
                    elif llm == "mistral":
                        llm_response = ask_mistral("mistral-large-2411",user_prompt,system_prompt)

                    with open("{}/{}.txt".format(output_dir,u), "w") as out:
                        if llm_response is None:
                            error_list.append("{}/{}.txt".format(output_dir,u))
                        else:
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
