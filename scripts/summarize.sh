# Purpose: Read the generated results and summarize them.
# Usage: bash scripts/summarize.sh

model_name_or_path=microsoft/phi-4
# model_name_or_path=deepseek-ai/DeepSeek-R1-Distill-Qwen-7B
prompt_types="direct,cot,causal-steps-fewshot,causal"

python scripts/summarize_results.py \
    --model_name_or_path $model_name_or_path \
    --result_dir output/$model_name_or_path/math_eval \
    --data_names gsm8k,minerva_math,mmlu_stem,cladder \
    --prompt_types $prompt_types \
    --num_test_sample 500