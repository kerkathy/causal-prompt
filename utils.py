import os
import json
import random
import json
import os
import numpy as np
from pathlib import Path
from typing import Iterable, Union, Any


def set_seed(seed: int = 42) -> None:
    np.random.seed(seed)
    random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    print(f"Random seed set as {seed}")


def load_jsonl(file: Union[str, Path]) -> Iterable[Any]:
    with open(file, "r", encoding="utf-8") as f:
        for line in f:
            try:
                yield json.loads(line)
            except:
                print("Error in loading:", line)
                exit()


def save_jsonl(samples, save_path):
    # ensure path
    folder = os.path.dirname(save_path)
    os.makedirs(folder, exist_ok=True)

    with open(save_path, "w", encoding="utf-8") as f:
        for sample in samples:
            f.write(json.dumps(sample) + "\n")
    print("Saved to", save_path)


def lower_keys(example):  
    new_example = {}  
    for key, value in example.items():  
        if key != key.lower():  
            new_key = key.lower()  
            new_example[new_key] = value  
        else:  
            new_example[key] = value  
    return new_example 


def load_prompt(data_name, prompt_type):
    if data_name in ['gsm_hard', 'svamp', 'tabmwp', 'asdiv', 'mawps']:
        data_name = "gsm8k"
    if data_name in ['math_oai', "hungarian_exam"]:
        data_name = "math"
    if data_name in ['sat_math']:
        data_name = "mmlu_stem"
    if prompt_type in ['platypus_fs']:
        prompt_type = "cot"
    if prompt_type in ['tool-integrated']:
        prompt_type = "tora"

    if prompt_type in ['cot', 'pal', 'tora', 'causal', 'causal-consistency', 'causal-steps-fewshot']:
        prompt_path = "./prompts/{}/{}.md".format(prompt_type, data_name)
        if not os.path.exists(prompt_path):
            prompt_path = "./prompts/{}.md".format(prompt_type)
        if os.path.exists(prompt_path):
            with open(prompt_path, 'r', encoding='utf-8') as fp:
                prompt = fp.read().strip() + "\n\n\n"
        else:
            print(f"Error: prompt file {prompt_path} not found")
            exit()
            # prompt = ""
    else:
        prompt = ""
    return prompt

def construct_prompt(example, data_name, args):
    # Base models
    if args.prompt_type in ["direct", "cot", "pal", "tool-integrated", "causal", "causal-consistency", "causal-steps-fewshot"]:
        demo_prompt = load_prompt(data_name, args.prompt_type)
        if args.prompt_type in ["direct", "cot", "causal", "causal-consistency"]:
            if data_name in ["minerva_math", "math", "math_oai", "mmlu_stem", "sat_math", "mathqa", "hungarian_exam"]:
                context = f"Problem:\n{example['question']}\nSolution:"
            else:
                context = f"Question: {example['question']}\nAnswer:"
            full_prompt = demo_prompt + context
        elif args.prompt_type == "causal-steps-fewshot":
            if data_name in ["minerva_math", "math", "math_oai", "mmlu_stem", "sat_math", "mathqa", "hungarian_exam"]:
                context = f"Problem:\n{example['question']}\n<causal_analysis>\n\n"
            else:
                context = f"Question: {example['question']}\n<causal_analysis>\n"
            full_prompt = demo_prompt + context
        elif args.prompt_type == "pal":
            context = f"Question: {example['question']}"
            full_prompt = demo_prompt + context
        elif args.prompt_type in ['tool-integreted']:
            context = f"Question: {example['question']}\n\nSolution:"
            full_prompt = demo_prompt + context

    # SFT models
    elif args.prompt_type in ['self-instruct', 'tora']:
        full_prompt = f"<|user|>\n{example['question']}\n<|assistant|>\n"
    elif args.prompt_type in ['self-instruct-boxed']:
        full_prompt = f"<|user|>\n{example['question']}\nEnclose the final answer using \\boxed{{}} otherwise it doesnt count.\n<|assistant|>\n"
    elif args.prompt_type == "wizard_zs":
        full_prompt = (
            "Below is an instruction that describes a task. "
            "Write a response that appropriately completes the request.\n\n"
            "### Instruction:\n{instruction}\n\n### Response: Let's think step by step."
        )
        full_prompt = full_prompt.format(instruction=example['question'])
    elif args.prompt_type == "deepseek-math":
        full_prompt = (
            "User: {instruction}\nPlease reason step by step, "
            "and put your final answer within \\boxed{{}} otherwise it doesnt count.\n\nAssistant:"
        )
        full_prompt = full_prompt.format(instruction=example['question'])
    elif args.prompt_type == "kpmath":
        full_prompt = (
            'User: Please reason step by step and put your final answer at the end '
            'with "The answer is: ".\n\n{instruction}\n\nAssistant:'
        )
        full_prompt = full_prompt.format(instruction=example['question'])
    elif args.prompt_type == "causal-instruct":
        full_prompt = (
            "User: Please solve math problems by carefully identifying the cause-and-effect relationships and constraints in the problem. "
            "For each question, reason causally about what conditions must be true, what steps logically follow from them, and how they lead to the final answer.\n"
            'Importantly, put your final answer with \\boxed{{}} otherwise it doesnt count.\n\n'
            "{instruction}\n\nAssistant:"
        )
        full_prompt = full_prompt.format(instruction=example['question'])
    elif args.prompt_type == "causal-steps":
        full_prompt = (
            'User: Think about this math problem using causal reasoning principles:\n\n'
            'Problem: {instruction}\n\n'
            '1) What are the key variables and their relationships?'
            '2) What do we want to determine (our "outcome")?'
            '3) What information do we have (our "data")?'
            '4) How can we systematically work from known to unknown?'
            '5) What mathematical "interventions" do we need?'
            '6) Solve step by step, checking causal consistency.'
            '7) Importantly, put your final answer with \\boxed{{}} otherwise it doesnt count.\n\n'
            "Assistant:"
        )
        full_prompt = full_prompt.format(instruction=example['question'])
    elif args.prompt_type == "cladder":
        full_prompt = (
            'Q: {instruction}\n'
            'Guidance: Address the question by following the steps below: \n'
            'Step 1) Extract the causal graph: Identify the causal graph that depicts the relationships in the scenario. The diagram should simply consist of edges denoted in "var1 -> var2" format, separated by commas.\n'
            'Step 2) Determine the query type: Identify the type of query implied by the main question. Choices include "marginal probability", "conditional probability", "explaining away effect", "backdoor adjustment set", "average treatment effect", "collider bias", "normal counterfactual question", "average treatment effect on treated", "natural direct effect" or "natural indirect effect". Your answer should only be a term from the list above, enclosed in quotation marks. \n'
            'Step 3) Formalize the query: Translate the query into its formal mathematical expression based on its type, utilizing the "do(·)" notation or counterfactual notations as needed. \n'
            'Step 4) Gather all relevant data: Extract all the available data. Your answer should contain nothing but marginal probabilities and conditional probabilities in the form "P(...)=..." or "P(...|...)=...", each probability being separated by a semicolon. Stick to the previously mentioned denotations for the variables. \n'
            'Step 5) Deduce the estimand using causal inference: Given all the information above, deduce the estimand using skills such as do-calculus, counterfactual prediction, and the basics of probabilities. Answer step by step. \n'
            'Step 6) Calculate the estimand: Insert the relevant data in Step 4 into the estimand, perform basic arithmetic calculations, and derive the final answer. There is an identifiable answer. Answer step by step.\n'
            'Based on all the reasoning above, put your final answer with \\boxed{{}} otherwise it doesnt count.\n\n'
            "Step 1):"
        )
        full_prompt = full_prompt.format(instruction=example['question'])
    else:
        raise NotImplementedError(args.prompt_type)
    return full_prompt

key_map = {
    "gt": "Ground Truth",
    "pred": "Prediction",
    "gt_cot": "Reference CoT",
    "score": "Score",
}

def show_sample(sample, print_all_preds=False):
    print("=="*20)
    for key in ["idx", "type", "level", "dataset"]:
        if key in sample:
            # capitalize
            print("{}: {}".format(key[0].upper() + key[1:], sample[key]))
    print("Question:", repr(sample['question']))
    if 'code' in sample:
        if print_all_preds:
            for code in sample['code']:
                print('-'*20)
                print("code:", code)
            print("Execution:", sample['report'])
        else:
            print("Solution:\n", sample['code'][0])
            print("Execution:", sample['report'][0])
    if 'pred' in sample:
        print("Prediction:", repr(sample['pred'][0]))
    for key in ["gt", "score", "unit", "gt_cot"]:
        if key in sample:
            _key  = key_map.get(key, key)
            print("{}: {}".format(_key, repr(sample[key])))
    print()
