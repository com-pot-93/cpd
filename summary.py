import os, sys
import json
import logging
import argparse
import csv
import time
import pandas as pd
from collections import Counter
#from iteration_utilities import flatten
#sys.path.append("./round_trip")
#sys.path.append("./model_evaluation/")
#import bpmn_similarity
#from round_trip.llm_connect.sap_hub_call import generate_with_timeout
#from merson.merson_converter import mermaid_to_json

def flatten_comprehension(matrix):
    return [item for row in matrix for item in row]

def main_pipeline(llm):
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()]
    )
    logger = logging.getLogger("{}Logger".format(llm.upper()))

    directory = './m2m_similarity/{}'.format(llm)  # set directory path
    full = []

    for root, _, files in os.walk(directory):
        for filename in files:  # loop through files in the current directory
            file_name = os.path.join(root, filename)
            print(filename)
            similarities = []
            meaning_sheet = pd.read_csv(file_name)
            meaning_prompts = meaning_sheet.iloc[:,2:8]
            pattern = filename.split(".")[0]
            output_dir = './summary/'.format(llm)
            mysum = [(filename)," "]
            for index, row in meaning_prompts.iterrows():
                if row['similarity'] == 1:
                   stat = True
                else:
                   stat = False
                if row['mapping'] == False:
                    temp = "{}".format(row['mapping'])
                elif row['meaning_status'] == False:
                    temp = "{},{}".format(row['mapping'],row['meaning_status'])
                else:
                    temp = "{},{},{},{}".format(row['mapping'],row['meaning_status'],row['epap'],stat)
                mysum.append(temp)
            res = list(Counter(mysum).items())
            res.remove((' ', 1))
            res.sort(key=lambda x: x[0])
            res.append(('',''))
            full.append(res)

    print(full)
    full = flatten_comprehension(full)
    summary = pd.DataFrame(full, columns =['1', 'count'])
    summary.to_csv("{}{}-general.csv".format(output_dir,llm), encoding='utf-8')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process models and text with retries and timeout.")
    parser.add_argument('--llm', type=str, required=True, help='Select llm mode: gpt or gemini')

    args = parser.parse_args()
    llm = args.llm.lower()
    if llm == 'gpt' or llm == 'gemini' or llm=='mistral':
        main_pipeline(llm)
    else:
        print('Please check selected llm model (only gpt or gemini are acceptable)!!!')
