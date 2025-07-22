import json
import glob
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_name_or_path", type=str)
    parser.add_argument("--result_dir", type=str)
    parser.add_argument("--data_names", type=str, default="gsm8k,minerva_math,svamp,asdiv,mawps")
    parser.add_argument("--split", type=str, default="test")
    parser.add_argument("--prompt_types", type=str, default=None, help="Comma-separated list of prompt types to summarize. If not provided, will auto-detect.")
    parser.add_argument("--num_test_sample", default=-1, type=int) # -1 for full data
    args = parser.parse_args()
    summarize_results(args.model_name_or_path, args.result_dir, args.data_names, args.split, args.prompt_types, args.num_test_sample)


def summarize_results(model_name_or_path, result_dir, data_names, split, prompt_types=None, num_test_sample=-1):
    data_list = data_names.split(',')
    
    # Auto-detect prompt types if not provided
    if prompt_types is None:
        prompt_types_set = set()
        for data_name in data_list:
            files = glob.glob(f"{result_dir}/{data_name}/{split}*metrics.json") # -1 to choose result for all data
            for file in files:
                # Extract prompt type from filename pattern: test_{prompt_type}_*_metrics.json
                filename = file.split('/')[-1]
                parts = filename.split('_')
                if len(parts) >= 2:
                    # Find the prompt type part (after split, before other parameters)
                    for i, part in enumerate(parts):
                        if part == split and i + 1 < len(parts):
                            prompt_type = parts[i + 1]
                            prompt_types_set.add(prompt_type)
                            break
        prompt_types_list = sorted(list(prompt_types_set))
        print(f"Auto-detected prompt types: {prompt_types_list}")
    else:
        prompt_types_list = prompt_types.split(',')
    
    # Collect results for table
    print(f"\nResults for {split} split:")
    print("=" * 80)

    # Table: rows = prompt types, columns = datasets, last column = avg
    table = []  # Each row: [prompt_type, acc1, acc2, ..., accN, avg]
    skipped_prompt_types = []

    for prompt_type in prompt_types_list:
        row = [prompt_type]
        accs = []
        missing_data = []
        for data_name in data_list:
            files = glob.glob(f"{result_dir}/{data_name}/{split}_{prompt_type}_{num_test_sample}_*metrics.json")
            if len(files) == 0:
                row.append(None)
                missing_data.append(data_name)
            else:
                if len(files) > 1:
                    print(f"Warning: Multiple metrics files found for {data_name} with prompt type {prompt_type}: {files}")
                print(f"Loading {files[0]}...")
                with open(files[0], 'r') as f:
                    metrics = json.load(f)
                    acc = metrics.get("acc", None)
                    row.append(acc)
                    if acc is not None:
                        accs.append(acc)
        # Always print the row, even if some data is missing
        avg_acc = sum(accs) / len(accs) if accs else 0.0
        row.append(avg_acc)
        table.append(row)

    print(f"\nModel: {model_name_or_path}")

    # Print table header
    col_names = data_list + ["avg"]
    pad = max([len(x) for x in prompt_types_list + col_names] + [8])
    header = ["Prompt Type".ljust(pad)] + [col.ljust(pad) for col in col_names]
    print(" | ".join(header))
    print("-" * (len(header) * (pad + 3)))

    # Print table rows
    for row in table:
        prompt_type = row[0].ljust(pad)
        accs = []
        for acc in row[1:]:
            if acc is None:
                accs.append("-".ljust(pad))
            else:
                accs.append(f"{acc:.1f}".ljust(pad))
        print(" | ".join([prompt_type] + accs))

    # No longer skipping prompt types, so no need to print skipped list


if __name__ == "__main__":
    main()
