import random
import os
import argparse
import time
from datetime import datetime
from tqdm import tqdm

from evaluate import evaluate
from utils import set_seed, load_jsonl, save_jsonl, construct_prompt
from parser import *
from trajectory import *
from data_loader import load_data
from math_eval import parse_question, parse_ground_truth, prepare_data


def build_prompt(data_name, args):
    examples, processed_samples, out_file = prepare_data(data_name, args)
    print("=" * 50)
    print("data:", data_name, " ,remain samples:", len(examples))
    if len(examples) > 0:
        print(examples[0])

    samples = []
    first_idx = examples[0]['idx'] if len(examples) > 0 else 0
    for example in tqdm(examples, total=len(examples)):
        idx = example['idx']

        # parse question and answer
        example['question'] = parse_question(example, data_name)
        gt_cot, gt_ans = parse_ground_truth(example, data_name)
        full_prompt = construct_prompt(example, data_name, args)

        # if idx == args.start:
        if idx == first_idx:
            print("Full prompt:\n", "-" * 50, "\n", full_prompt, "\n" + "-" * 50)
            # Save the complete prompt example to a file
            prompt_file = out_file.replace(".jsonl", "_prompt_example.txt")
            with open(prompt_file, "w", encoding="utf-8") as f:
                f.write(f"Dataset: {data_name}\n")
                f.write(f"Prompt Type: {args.prompt_type}\n")
                f.write(f"Model: {args.model_name_or_path}\n")
                f.write(f"Example Index: {idx}\n")
                f.write(f"Temperature: {args.temperature}\n")
                f.write("=" * 80 + "\n")
                f.write("COMPLETE PROMPT:\n")
                f.write("=" * 80 + "\n")
                f.write(full_prompt)
                f.write("\n" + "=" * 80 + "\n")
                f.write(f"Ground Truth Answer: {gt_ans}\n")
            print(f"Saved prompt example to: {prompt_file}")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_names", default="gsm8k,math", type=str)
    parser.add_argument("--data_dir", default="./data", type=str)
    parser.add_argument("--model_name_or_path", default="gpt-4", type=str)
    parser.add_argument("--output_dir", default="./output", type=str)
    parser.add_argument("--prompt_type", default="tool-integrated", type=str)
    parser.add_argument("--split", default="test", type=str)
    parser.add_argument("--num_test_sample", default=-1, type=int) # -1 for full data
    parser.add_argument("--seed", default=0, type=int)
    parser.add_argument("--start", default=0, type=int)
    parser.add_argument("--end", default=-1, type=int)
    parser.add_argument("--temperature", default=0, type=float)
    parser.add_argument("--n_sampling", default=1, type=int)
    parser.add_argument("--top_p", default=1, type=float)
    parser.add_argument("--max_tokens_per_call", default=4096, type=int)
    parser.add_argument("--shuffle", action="store_true")
    parser.add_argument("--use_vllm", action="store_true")
    parser.add_argument("--save_outputs", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--use_safetensors", action="store_true")
    parser.add_argument("--use_openai_api", action="store_true", help="Use OpenAI API for vLLM")
    parser.add_argument("--openai_base_url", type=str, default=None, help="Custom base URL for OpenAI API")
    parser.add_argument("--api_key", type=str, default=None, help="API key for OpenAI API")
    args = parser.parse_args()
    args.top_p = 1 if args.temperature == 0 else args.top_p
    return args

def main():
    args = parse_args()
    print("Arguments:", args)

    # after split by , there are multiple prompt types, then we will run the main function for each prompt type
    all_prompt_types = args.prompt_type.split(',')
    print("Prompt types:", all_prompt_types)

    for prompt_type in all_prompt_types:
        args.prompt_type = prompt_type.strip()
        data_names = args.data_names.split(",")
        for data_name in data_names:
            print(f"Processing dataset: {data_name}")
            out_file = os.path.join(args.output_dir, f"{data_name}_{args.prompt_type}.jsonl")
            if not os.path.exists(args.output_dir):
                os.makedirs(args.output_dir)
            if os.path.exists(out_file) and not args.overwrite:
                print(f"Output file {out_file} already exists. Skipping...")
                continue

            examples = load_data(data_name, args.split)
            if len(examples) == 0:
                print(f"No examples found for dataset {data_name}. Skipping...")
                continue

            build_prompt(data_name, args)
            save_jsonl(examples, out_file)

if __name__ == "__main__":
    main()