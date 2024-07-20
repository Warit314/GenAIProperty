docker run -it -p 8000:8000 --gpus all vllms


huggingface-cli login

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

write toke n
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

python3 -m vllm.entrypoints.openai.api_server --port 8000 --model google/gemma-2b \
--tensor-parallel-size 1 --dtype half

docker run --gpus all -v C:\Users\Warit\.cache\huggingface:/root/.cache/huggingface --env "HUGGING_FACE_HUB_TOKEN=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" -p 8000:8000 --ipc=host vllm/vllm-openai:latest --model /root/.cache/huggingface/hub/gemma-2b-it --dtype half 