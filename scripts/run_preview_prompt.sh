# set -x

export HF_ENDPOINT="https://hf-mirror.com"
# export TRANSFORMERS_OFFLINE=1
# export HF_DATASETS_OFFLINE=1

PROMPT_TYPE=cot,causal-steps-fewshot,causal
# MODEL_NAME_OR_PATH=$2
# PROMPT_TYPE=causal-consistency
# PROMPT_TYPE=causal-steps,causal-steps-fewshot

# MODEL_NAME_OR_PATH=DeepSeek-R1-Distill-Qwen-7B
# MODEL_NAME_OR_PATH="microsoft/phi-4"
MODEL_NAME_OR_PATH="deepseek-ai/DeepSeek-R1-Distill-Qwen-7B"
# MODEL_NAME_OR_PATH="Qwen/Qwen2.5-7B-Instruct"
# MODEL_NAME_OR_PATH="Qwen/Qwen2.5-7B"
URL="https://llmapi.paratera.com/v1/"


OUTPUT_DIR=./output/${MODEL_NAME_OR_PATH}/math_eval
DATA_NAMES="cladder"
# DATA_NAMES="gsm8k,minerva_math,svamp,asdiv,mawps,tabmwp,mathqa,mmlu_stem,sat_math,cladder"
SPLIT="test"
NUM_TEST_SAMPLE=3


# gpu setting
CUDA_VISIBLE_DEVICES=0,1 TOKENIZERS_PARALLELISM=true \
python3 -u preview_prompt.py \
    --model_name_or_path ${MODEL_NAME_OR_PATH} \
    --output_dir ${OUTPUT_DIR} \
    --data_names ${DATA_NAMES} \
    --split ${SPLIT} \
    --prompt_type ${PROMPT_TYPE} \
    --num_test_sample ${NUM_TEST_SAMPLE} \
    --seed 0 \
    --temperature 0 \
    --n_sampling 1 \
    --top_p 1 \
    --start 0 \
    --end -1 \
    --use_vllm \
    --save_outputs \
    --overwrite \
    # --use_openai_api \
    # --openai_base_url ${URL} \
    # --api_key ${PARATERA_API_KEY} \