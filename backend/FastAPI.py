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


# async def generate_response(message,query_result=None):
#     if query_result:
#         prompt = PromptTemplate(input_variables=["message"], template=Prompt.gemini_prompt_answer)

#         chain= prompt | llm

#         async for chunk in chain.astream({"message": message, "query_result":query_result}):
            
#             yield  chunk

# async def generate_query(message):
#     # Set up a parser + inject instructions into the prompt template.
#     parser = JsonOutputParser()

#     prompt = PromptTemplate(input_variables=["message"], template=Prompt.gemini_prompt_query)

#     chain= prompt | llm | parser

#     result = chain.invoke({"message": message})
    
#     return result

# async def extract_query(llm_result:dict):
#     property_dict=schema
#     #replace value in a dict
#     for key,value in llm_result.items():
#         if key in schema:
#             property_dict[key]=value

#     # Base SQL query
#     query = "SELECT name,title,details, price, routed_distance, routed_time, nearest_stations,pool,sauna,fitness,jacuzzi,keycard,laundry,parking,shuttle,allowPet,security,restaurant FROM sample_data WHERE 1=1"

#     # Add conditions based on the dictionary values
#     if property_dict["name"] is not None and not False:
#         query += f" AND name LIKE '%{property_dict['name']}%'"
#     if property_dict["price_less_than"] is not None:
#         query += f" AND price < {property_dict['price_less_than']}"
#     if property_dict["routed_distance"] is not None:
#         query += f" AND routed_distance = '{property_dict['routed_distance']}'"
#     if property_dict["routed_time"] is not None:
#         query += f" AND routed_time = '{property_dict['routed_time']}'"
#     if property_dict["nearest_stations"] is not None:
#         query += f" AND nearest_stations = '{property_dict['nearest_stations']}'"
#     if property_dict["pool"]:
#         query += f" AND pool = {property_dict['pool']}"
#     if property_dict["sauna"]:
#         query += f" AND sauna = {property_dict['sauna']}"
#     if property_dict["fitness"]:
#         query += f" AND fitness = {property_dict['fitness']}"
#     if property_dict["jacuzzi"]:
#         query += f" AND jacuzzi = {property_dict['jacuzzi']}"
#     if property_dict["keycard"]:
#         query += f" AND keycard = {property_dict['keycard']}"
#     if property_dict["laundry"]:
#         query += f" AND laundry = {property_dict['laundry']}"
#     if property_dict["parking"]:
#         query += f" AND parking = {property_dict['parking']}"
#     if property_dict["shuttle"]:
#         query += f" AND shuttle = {property_dict['shuttle']}"
#     if property_dict["allowPet"]:
#         query += f" AND allowPet = {property_dict['allowPet']}"
#     if property_dict["security"]:
#         query += f" AND security = {property_dict['security']}"
#     if property_dict["restaurant"]:
#         query += f" AND restaurant = {property_dict['restaurant']}"

#     query+=" LIMIT 4"

#     logging.debug(f"QUERY : {query}")

#     # Print the final 
#     sqlite_db = 'database.db' 
#     return query_sqlite(sqlite_db,query)

# # Function to query data from SQLite and print it
# def query_sqlite(sqlite_db, query):
#     # Connect to SQLite database
#     conn = sqlite3.connect(sqlite_db)
#     cursor = conn.cursor()

#     # Execute the query
#     cursor.execute(query)

#     # Fetch column names
#     column_names = [description[0].upper() for description in cursor.description]

#     # Fetch all rows from the executed query
#     rows = cursor.fetchall()

#     results_list = []
#     # Combine column names with row values
#     for row in rows:
#         result = {column_names[i]: row[i] for i in range(len(column_names))}
#         results_list.append(result)

#     # Close the connection
#     conn.close()

#     logging.debug(f"RESULT LIST: {results_list}")
#     return results_list