# Inspiration
- A Property Chatbot- I decided to do project about finding condo since i was recently finding one.
- The user pain point is having through scroll through a lot of facebook post or the web to find an actually good condo.
- Another problem ( I'm not sure how  to solve it yet.) is Property Agent seems to not updating their post so most of the property on the website is likely already rented. Having realize this problem - i think it would be easier to visualize where each condo is and Since i don't want to read through hundreds of post. I created an LLM to read for me instead

# Installation
this project use vllm for text-embedding and fast inferencing.
Since my pc is windows and vllm require linux. i need to run it through WSL so:
```
docker pull vllm/vllm-openai:latest
```
you can use my docker compose file to start the deploying the model and start my backend and frontend
```
docker compose up --build
```
*note that this use huggingface token please replace with yours*

The project is intended to be a prove of concept to use llm to generate SQL query.
Since this is POC i use sqlite for the database. 

# Steps of how it works:
Basically i use langchain and VLLM to use the model to generate a SQL query to find details about the property. Using Fast API as Api endpoints and fetch the data through the frontend using streamlit (for rapid development) 

The reason i choose SQL query because the volume of the data, RAG is more suitable to use with books and other type of data.

# Additional notes - Design flaw -Limitation
- *the query generation is very limited due to limitation from my gpus (RTX2060) I don't have bigger vram to server bigger model So i choose to only use gemma 2b it*
- *Since i have no api for the real data, I don't have data of nearest BTS, MRT or distance to them. This is the biggest flaw in my project, which led to the potential search for only the name of the condo. Where the user already know which condo do they want*
