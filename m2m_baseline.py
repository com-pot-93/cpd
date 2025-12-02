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

    directory = os.path.join('./baseline/',llm)

    patterns= os.listdir(directory)
    for p in patterns:
        files = os.path.join(directory,p)
        if os.path.isdir(files):
            frame = {}
            ids = []
            similarities = []
            print(files)
            #correct expected model
            inputfile = "./EAO/{}.txt".format(p)
            mermaid = open(inputfile, "r")
            expected_bpmn = mermaid.read()
            expected_json = json.loads(mermaid_to_json(expected_bpmn))

            for f in range (0,64):
                ids.append(f)
                filename = "{}.txt".format(f)
                filepath = os.path.join(files,filename)
                if os.path.exists(filepath):
                    generated = open(filepath, "r")
                    generated_bpmn = generated.read()
                    generated_json = json.loads(mermaid_to_json(generated_bpmn))
                    try:
                        similarity_score = bpmn_similarity.calculate_similarity_scores(
                            expected_json, generated_json, method="dice", similarity_threshold=0.95
                        )[0]["overall"]
                    except:
                        similarity_score = 0
                else:
                    similarity_score = 0
                similarities.append(similarity_score)
        frame['ids'] = ids
        frame['similarity'] = similarities
        excel = pd.DataFrame.from_dict(frame)
        excel.to_csv("./m2m_baseline/{}/{}.csv".format(llm,p), encoding='utf-8')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process models and text with retries and timeout.")
    parser.add_argument('--llm', type=str, required=True, help='Select llm mode: gpt or gemini')

    args = parser.parse_args()
    llm = args.llm.lower()
    if llm == 'gpt' or llm == 'gemini' or llm=='mistral':
        main_pipeline(llm)
    else:
        print('Please check selected llm model (only gpt or gemini are acceptable)!!!')
