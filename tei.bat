@echo off
docker run --gpus all -v C:\Users\Warit\.cache\huggingface:/root/.cache/huggingface --env "HUGGING_FACE_HUB_TOKEN=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" -p 8000:8000 --ipc=host vllm/vllm-openai:latest --model /root/.cache/huggingface/hub/gemma-2b-it --dtype half
