set -ex

# PROMPT_TYPE=$1
# MODEL_NAME_OR_PATH=$2
PROMPT_TYPE=direct
MODEL_NAME_OR_PATH=DeepSeek-R1-Distill-Qwen-7B
URL="https://llmapi.paratera.com/v1/"

# ======= Base Models =======
# PROMPT_TYPE="cot" # direct / cot / pal / tool-integrated / causal-bare / causal
# MODEL_NAME_OR_PATH=${HF_MODEL_DIR}/mistral/Mistral-7B-v0.1
# MODEL_NAME_OR_PATH=${HF_MODEL_DIR}/llemma/llemma_7b
# MODEL_NAME_OR_PATH=${HF_MODEL_DIR}/internlm/internlm2-math-base-7b
# MODEL_NAME_OR_PATH=${HF_MODEL_DIR}/deepseek/deepseek-math-7b-base


# ======= SFT Models =======
# PROMPT_TYPE="deepseek-math" # self-instruct / tora / wizard_zs / deepseek-math / kpmath
# MODEL_NAME_OR_PATH=${HF_MODEL_DIR}/deepseek/deepseek-math-7b-rl
# MODEL_NAME_OR_PATH=${HF_MODEL_DIR}/deepseek/deepseek-math-7b-instruct


OUTPUT_DIR=${MODEL_NAME_OR_PATH}/math_eval
DATA_NAMES="gsm8k"
# DATA_NAMES="gsm8k,minerva_math,svamp,asdiv,mawps,tabmwp,mathqa,mmlu_stem,sat_math"
SPLIT="test"
NUM_TEST_SAMPLE=-1


# single-gpu
CUDA_VISIBLE_DEVICES=0 TOKENIZERS_PARALLELISM=false \
python3 -u math_eval.py \
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
    --use_openai_api \
    --openai_base_url ${URL} \
    --api_key ${PARATERA_API_KEY} \
    --overwrite \
