## Description
This repository contains evaluation tables and code for conversational model redesign (cpd) approach.

[AAO](./AAO) : Actual Agent Output - process models generated after meaning was applied to the input models

[EAO](./EAO) : Expected Agent Output - process models that were used for the survey to obtain wording

[baseline](./baseline) : contains directly adapted process models for each wording

[derive](./derive) : contains derived meaning for each wording

[identify](./identify) : contains identified pattern for each wording

[input](./input) : Input Process Models - process models that were used for the survey to obtain wording. Models to which meaning is applied

[m2m_baseline](./m2m_baseline) : contains for each wording similarity scores between each corresponding AAO (using baseline approach) and EAO

[m2m_similarity](./m2m_similarity) : contains for each wording similarity scores between each corresponding AAO and EAO

[prompts](./prompts) : contains prompts for each stage of the cpd approach

[summary](./summary) : contains average results over 3 llms for each outcome of the evaluation 

[survey](./survey) : contains survey results, i.e., multiple wordings for each corresponding pattern


For model-to-model comparison [model_evaluation](./model_evaluation) we utilise similarity metrics implemented in another git-hub repo: https://github.com/SAP-samples/llm-round-trip-correctness/tree/main/model_evaluation.
[round_trip](./merson) is also partially a part of this repo. 

[round_trip](./merson) : contains code to make a call to the llm. 

[merson](./merson) : model converter between mermaid,js and simplified json required by model eveluation module


Impotant: for privite use to make a call to the llm user requires own API key. 

For more information rely on official documentation.

For all runs across all LLMs, we consistently used a temperature of 0. 

However, due to the nature of LLMs, results can still vary between repetitions. Therefore, all artifacts generated during the experiment are provided in the repository. Feel free to use them.

## Requirements and set up

The requirements are in this [pyproject.toml](./pyproject.toml) file. After cloning the repository, run:

```shell
poetry install
```

## Getting started

To run the pipeline, use a command similar to this:
```shell
python <script>.py --llm <llm-name> 
```

