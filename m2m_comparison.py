import os, sys
import json
import logging
import argparse
import csv
import time
import pandas as pd
sys.path.append("./round_trip")
sys.path.append("./model_evaluation/")
import bpmn_similarity
from merson.merson_converter import mermaid_to_json

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
            print(filename)
            similarities = []
            meaning_status = []
            meaning_sheet = pd.read_csv(file_name)
            meaning_prompts = meaning_sheet.iloc[:,4:]
            meaning_prompts = meaning_prompts['meaning'].to_list()
            pattern = filename.split("-")[1]
            output_dir = './AAO/{}/{}'.format(llm,pattern)
            inputfile = "./EAO/{}.txt".format(pattern)
            mermaid = open(inputfile, "r")
            expected_bpmn = mermaid.read()
            expected_json = json.loads(mermaid_to_json(expected_bpmn))
            for m in range(0,len(meaning_prompts)):
                meaning = meaning_prompts[m]
                if isinstance(meaning, str):
                    meaning = meaning.strip()
                    if meaning != "NA" and meaning.lower() != "false":
                        stat = True
                    else:
                        stat = False
                    generated = open("{}/{}.txt".format(output_dir,m), "r")
                    print("{}/{}.txt".format(output_dir,m))
                    generated_bpmn = generated.read()
                    #print("generated BPMN: ", generated_bpmn)
                    generated_json = json.loads(mermaid_to_json(generated_bpmn))
                    try:
                        similarity_score = bpmn_similarity.calculate_similarity_scores(
                            expected_json, generated_json, method="dice", similarity_threshold=0.95
                        )[0]["overall"]
                    except:
                        similarity_score = 0

                similarities.append(similarity_score)
                meaning_status.append(stat)

            meaning_sheet['meaning_status'] = meaning_status
            meaning_sheet['similarity'] = similarities
            meaning_sheet.to_csv("./m2m_similarity/{}/{}.csv".format(llm,pattern), encoding='utf-8')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process models and text with retries and timeout.")
    parser.add_argument('--llm', type=str, required=True, help='Select llm mode: gpt or gemini')

    args = parser.parse_args()
    llm = args.llm.lower()
    if llm == 'gpt' or llm == 'gemini' or llm=='mistral':
        main_pipeline(llm)
    else:
        print('Please check selected llm model (only gpt or gemini are acceptable)!!!')
