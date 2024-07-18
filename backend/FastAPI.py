from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from langchain_community.llms import VLLMOpenAI
from langchain_core.prompts.prompt import PromptTemplate
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from starlette.responses import StreamingResponse
import json
from backend.model import PropertyListing
from langchain_core.output_parsers import JsonOutputParser
import json
import re
import sqlite3
import logging
from fastapi.middleware.cors import CORSMiddleware
logging.basicConfig(level=logging.DEBUG)
#Default model
#google/gemma-2b-it
# TinyLlama/TinyLlama-1.1B-Chat-v1.0
llm = VLLMOpenAI(
    
    openai_api_key="EMPTY",
    openai_api_base="http://localhost:8000/v1",
    model_name="/root/.cache/huggingface/hub/gemma-2b-it",
    streaming=True,
    temperature=0.0,
    verbose=True,
    max_tokens=4096,
    callbacks=[StreamingStdOutCallbackHandler()]
)

#schema
schema={
  "name": None,
  "price_less_than": None,
  "routed_distance": None,
  "routed_time": None,
  "nearest_stations": None,
  "pool": None,
  "sauna": None,
  "fitness": None,
  "jacuzzi": None,
  "keycard": None,
  "laundry": None,
  "parking": None,
  "shuttle": None,
  "allowPet": None,
  "security": None,
  "restaurant": None
}





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

# Define an endpoint to create an item
@app.post("/chat_bot/")
async def chat_bot(message: Message):

    return StreamingResponse(generate_response(message.message),media_type='application/json')

#for test and debug
@app.post("/generate_query/")
async def chat_bot_query(message: Message):
    response = await generate_query(message.message)
    return response



@app.post("/generate_query_and_query_sqlite")
async def generate_query_and_query_sqlite(message: Message):
    #generate query with llm
    response = await generate_query(message.message)

    #then return results from sqlite query
    return await make_sqlite_query(response)

@app.post("/full_flow")
async def full_flow(message: Message):
    query_result = await generate_query_and_query_sqlite(message)
    return StreamingResponse(generate_response(message.message,query_result),media_type='application/json')

gemini_prompt_answer="""
<bos><start_of_turn>system
You are a property expert tasked with helping clients find rental properties in Bangkok, Thailand. 
You have access to detailed listings of various properties, including their names, locations, prices, features, and contact information for agents. 
Below is property data, leverage this to provide comprehensive recommendations and insights:
<<Property Data>>
{query_result}
<<End of Property Data>>

You MUST use only this information to response to the user, DO NOT use other information

<end_of_turn>
<start_of_turn>user
{message}<end_of_turn>
<start_of_turn>model
"""
gemini_prompt_query="""
<bos><start_of_turn>system
You are an intelligent assistant tasked with extracting data for property listings. Below is the data model that will be used to create an SQL query. 
Your task is to:
 - Extract data from the user's question.
 - Format the extracted data in JSON, with keys matching the variable names from the given schema.
<<Schema>>
name: Optional[str] - Property name in English (if available)
price_less_than: Optional[int] - Rental price per month less than the specified amount (if available)
routed_distance: Optional[str] - Distance to key locations (if available)
routed_time: Optional[str] - Time to key locations (if available)
nearest_stations: Optional[str] - Nearest public transport stations (if available)
pool: Optional[bool] - Indicates if the property has a pool (if available)
sauna: Optional[bool] - Indicates if the property has a sauna (if available)
fitness: Optional[bool] - Indicates if the property has a fitness center (if available)
jacuzzi: Optional[bool] - Indicates if the property has a jacuzzi (if available)
keycard: Optional[bool] - Indicates if the property has keycard access (if available)
laundry: Optional[bool] - Indicates if the property has laundry facilities (if available)
parking: Optional[bool] - Indicates if the property has parking (if available)
shuttle: Optional[bool] - Indicates if the property has a shuttle service (if available) 
allowPet: Optional[bool] - Indicates if pets are allowed(if available) 
security: Optional[bool] - Indicates if the property has security services (if available)
restaurant: Optional[bool] - Indicates if the property has a restaurant (if available)

You MUST only return the result in json format.
<end_of_turn>
<start_of_turn>user
<<User question>> 
{message}<end_of_turn>
<start_of_turn>model
"""


async def generate_response(message,query_result=None):
    if query_result:
        prompt = PromptTemplate(input_variables=["message"], template=gemini_prompt_answer)

        chain= prompt | llm

        async for chunk in chain.astream({"message": message, "query_result":query_result}):
            
            yield  chunk
    else:
        prompt = PromptTemplate(input_variables=["query_result","message"], template=gemini_prompt_query)

        chain= prompt | llm

        async for chunk in chain.astream({"message": message}):
            
            yield chunk



async def generate_query(message):
    # Set up a parser + inject instructions into the prompt template.
    parser = JsonOutputParser()

    prompt = PromptTemplate(input_variables=["message"], template=gemini_prompt_query)

    chain= prompt | llm | parser

    result = chain.invoke({"message": message})
    
    return result

async def make_sqlite_query(llm_result:dict):
    property_dict=schema
    #replace value in a dict
    for key,value in llm_result.items():
        if key in schema:
            property_dict[key]=value

    # Base SQL query
    query = "SELECT name,title,details, price, routed_distance, routed_time, nearest_stations,pool,sauna,fitness,jacuzzi,keycard,laundry,parking,shuttle,allowPet,security,restaurant FROM sample_data WHERE 1=1"

    # Add conditions based on the dictionary values
    if property_dict["name"] is not None and not False:
        query += f" AND name LIKE '%{property_dict['name']}%'"
    if property_dict["price_less_than"] is not None:
        query += f" AND price < {property_dict['price_less_than']}"
    if property_dict["routed_distance"] is not None:
        query += f" AND routed_distance = '{property_dict['routed_distance']}'"
    if property_dict["routed_time"] is not None:
        query += f" AND routed_time = '{property_dict['routed_time']}'"
    if property_dict["nearest_stations"] is not None:
        query += f" AND nearest_stations = '{property_dict['nearest_stations']}'"
    if property_dict["pool"]:
        query += f" AND pool = {property_dict['pool']}"
    if property_dict["sauna"]:
        query += f" AND sauna = {property_dict['sauna']}"
    if property_dict["fitness"]:
        query += f" AND fitness = {property_dict['fitness']}"
    if property_dict["jacuzzi"]:
        query += f" AND jacuzzi = {property_dict['jacuzzi']}"
    if property_dict["keycard"]:
        query += f" AND keycard = {property_dict['keycard']}"
    if property_dict["laundry"]:
        query += f" AND laundry = {property_dict['laundry']}"
    if property_dict["parking"]:
        query += f" AND parking = {property_dict['parking']}"
    if property_dict["shuttle"]:
        query += f" AND shuttle = {property_dict['shuttle']}"
    if property_dict["allowPet"]:
        query += f" AND allowPet = {property_dict['allowPet']}"
    if property_dict["security"]:
        query += f" AND security = {property_dict['security']}"
    if property_dict["restaurant"]:
        query += f" AND restaurant = {property_dict['restaurant']}"

    query+=" LIMIT 5"

    logging.debug(f"QUERY : {query}")

    # Print the final 
    sqlite_db = 'database.db' 
    return query_sqlite(sqlite_db,query)

# Function to query data from SQLite and print it
def query_sqlite(sqlite_db, query):
    # Connect to SQLite database
    conn = sqlite3.connect(sqlite_db)
    cursor = conn.cursor()

    # Execute the query
    cursor.execute(query)

    # Fetch column names
    column_names = [description[0].upper() for description in cursor.description]

    # Fetch all rows from the executed query
    rows = cursor.fetchall()

    results_list = []
    # Combine column names with row values
    for row in rows:
        result = {column_names[i]: row[i] for i in range(len(column_names))}
        results_list.append(result)

    # Close the connection
    conn.close()

    logging.debug(f"RESULT LIST: {results_list}")
    return results_list