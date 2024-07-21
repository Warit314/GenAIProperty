from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from langchain_core.prompts.prompt import PromptTemplate
from starlette.responses import StreamingResponse
from langchain_core.output_parsers import JsonOutputParser
from backend.Prompt import Prompt
from backend.main import Controllers
from fastapi.middleware.cors import CORSMiddleware


# Create the FastAPI instance
app = FastAPI()


# Allow all origins (for development purposes only)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)


# Define a data model using Pydantic
class Message(BaseModel):
    message: str

class ChatbotMessages(BaseModel):
    message: str
    query_result : Optional[str]

# chatbot
@app.post("/chat_bot")
async def chat_bot(message: ChatbotMessages):

    return StreamingResponse(Controllers.generate_response(message.message,message.query_result),media_type='application/json')

#for test and debug
@app.post("/generate_query")
async def chat_bot_query(message: Message):
    response = await Controllers.generate_query(message.message)
    return response

@app.post("/generate_query_and_query_sqlite")
async def generate_query_and_query_sqlite(message: Message):
    #generate query with llm
    response = await Controllers.generate_query(message.message)

    #then return results from sqlite query
    return await Controllers.extract_query(response)

@app.get("/Get_map_plot_data")
async def Get_map_plot_data():
    query= "SELECT name,latitude, longitude FROM sample_data"
    result = Controllers.query_sqlite("database.db", query)

    return result

@app.post("/Query_Sqlite")
def Query_Sqlite(query:Message):
    result = Controllers.query_sqlite("database.db", query.message)

    return result