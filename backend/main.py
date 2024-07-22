from langchain_community.llms import VLLMOpenAI
from langchain_core.prompts.prompt import PromptTemplate
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_core.output_parsers import JsonOutputParser
from backend.Prompt import Prompt
import sqlite3
import logging
import json

logging.basicConfig(level=logging.DEBUG)
#Default model
# google/gemma-2b-it
# TinyLlama/TinyLlama-1.1B-Chat-v1.0
llm = VLLMOpenAI(
    
    openai_api_key="EMPTY",
    openai_api_base="http://model:8000/v1",
    model_name="/root/.cache/huggingface/hub/gemma-2b-it",
    streaming=True,
    temperature=0.6,
    verbose=True,
    frequency_penalty=0.5,
    max_tokens=3000,
    callbacks=[StreamingStdOutCallbackHandler()]
)

query_former_llm = VLLMOpenAI(
    
    openai_api_key="EMPTY",
    openai_api_base="http://model:8000/v1",
    model_name="/root/.cache/huggingface/hub/gemma-2b-it",
    streaming=True,
    temperature=0.0,
    top_p= 0.1,
    frequency_penalty=0.0,
    # top_k=0.1,
    verbose=True,
    max_tokens=2000,
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

class Controllers():

    @staticmethod
    async def generate_response(message,query_result=None):
        if query_result:

            prompt = PromptTemplate(input_variables=["message"], template=Prompt.gemini_prompt_answer)

            chain= prompt | llm

            async for chunk in chain.astream({"message": message, "query_result":query_result}):
                
                yield  chunk

    @staticmethod
    async def generate_query(message):
        # Set up a parser + inject instructions into the prompt template.
        parser = JsonOutputParser()

        prompt = PromptTemplate(input_variables=["message"], template=Prompt.gemini_prompt_query)

        chain= prompt | query_former_llm | parser

        result = chain.invoke({"message": message})
        
        return result

    @staticmethod
    async def extract_query(llm_result:dict):
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

        query+=" LIMIT 3"

        logging.debug(f"QUERY : {query}")

        # Print the final 
        sqlite_db = 'database.db' 
        return Controllers.query_sqlite(sqlite_db,query)

    @staticmethod
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