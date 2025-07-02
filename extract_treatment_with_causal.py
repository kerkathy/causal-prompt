import json

# Set your file paths here
treatment_prompt_type = "causal"
control_prompt_type = "cot"
data_size = -1
model_name_or_path = "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B"
dataset_name = "minerva_math"

treatment_path = f"{model_name_or_path}/math_eval/{dataset_name}/test_{treatment_prompt_type}_{data_size}_seed0_t0.0_s0_e-1.jsonl"
control_path = f"{model_name_or_path}/math_eval/{dataset_name}/test_{control_prompt_type}_{data_size}_seed0_t0.0_s0_e-1.jsonl"

# Choose the unique key to match items (update if needed)
UNIQUE_KEY = "idx"

def load_jsonl(path):
    with open(path, "r") as f:
        return [json.loads(line) for line in f]

def main():
    treatment = load_jsonl(treatment_path)
    control = load_jsonl(control_path)

    # Only consider treatment items mentioning "causal" in code
    filtered_treatment = [
        item for item in treatment
        if "code" in item and "causal" in item["code"][0]
    ]

    # Build control lookup table by unique key
    control_lookup = {item[UNIQUE_KEY]: item for item in control}

    # Confusion matrix: (control_score, treatment_score) -> count
    matrix = {
        (False, False): [],
        (False, True): [],
        (True, False): [],
        (True, True): [],
    }

    for t_item in filtered_treatment:
        key = t_item[UNIQUE_KEY]
        t_score = bool(t_item["score"][0])
        c_item = control_lookup.get(key)
        if c_item is not None:
            c_score = bool(c_item["score"][0])
            matrix[(c_score, t_score)].append(t_item[UNIQUE_KEY])

    print("Confusion Matrix (control -> treatment):")
    print("             | Treatment False | Treatment True")
    print("-------------+-----------------+---------------")
    print(f"Control False | {len(matrix[(False, False)]:>15)} | {len(matrix[(False, True)]):>13}")
    print(f"Control True  | {len(matrix[(True, False)]:>15)} | {len(matrix[(True, True)]:>13)}")
    print(f"Total: {sum(len(v) for v in matrix.values())}, should be {len(filtered_treatment)}")

    for (c_score, t_score), idx_list in matrix.items():
        if c_score != t_score:
            print(f"Control {c_score} -> Treatment {t_score} : {idx_list}")

if __name__ == "__main__":
    main()