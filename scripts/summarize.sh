# run summarize_result.py

model_name_or_path=deepseek-ai/DeepSeek-R1-Distill-Qwen-7B

python3 summarize_result.py \
    --input_dir output/ \
    --model_name_or_path $model_name_or_path \
    # --output_file results/summary.txt \