model_name_or_path=phi-4
# model_name_or_path=deepseek-ai/DeepSeek-R1-Distill-Qwen-7B

python scripts/summarize_results.py \
    --result_dir output/$model_name_or_path/math_eval \
    --data_names gsm8k,minerva_math,mmlu_stem