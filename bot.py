import os

from dotenv import load_dotenv
from openai import AsyncOpenAI
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.providers.google_gla import GoogleGLAProvider

from schema import CheckResponse, ExtractResponse, SQLResponse
from tools import (AgentContext, check_prompt_filtering, check_user_permission,
                   get_current_time)

load_dotenv()

token = os.environ["GEMINI_KEY"]
endpoint = os.environ["BASE_URL"]
model_name = os.environ["MODEL"]


model = GeminiModel(model_name, provider=GoogleGLAProvider(api_key=token))


def create_perimiter_agent() -> Agent:
    perimiter_agent = Agent(
        system_prompt="""
        You are a helpful assistant that processes user queries while enforcing strict access control and prompt filtering. For every incoming query, always follow this exact sequence:

        Use the "check_prompt_filtering" tool to evaluate the query for safety and appropriateness.
        If the result is OK, proceed to step 2.

        If the result is not OK, respond with:
        "You are not allowed to access this information."
        and stop further processing.

        Use the "check_user_permission" tool to check if the user has permission to access the requested information. If the user is not allowed to access the information, respond with:
        
        can_proceed: true
        message: "You are allowed to access this information."

        If the result is not allowed, respond with:
        can_proceed: false
        message: "You are not allowed to access this information."

        This process must be executed for every user query without exception.
        """,
        model=model,
        deps_type=AgentContext,
        tools=[check_prompt_filtering, check_user_permission],
        output_type=CheckResponse,
    )

    return perimiter_agent


def create_sql_agent() -> Agent:
    schema = open("dbschema.txt", "r").read()
    agent = Agent(
        model,
        system_prompt=f"""
You are a helpful assistant specialising in data analysis and SQL.
Answer the questions by providing SQL code that is compatible with the provided schema.

**Follow these rules:**
* Use correct table names and column names from the schema.
* Find the relevant attributes and relationships in the schema.
* Find the table join conditions based on the schema and the query.
* Only include columns and conditions relevant to the request.
* If the request is ambiguous, make reasonable assumptions and mention them in a comment above the query.
* The user won't specify the table names, you need to infer them from the schema and the request.
* Return only the SQL query, no explanation.

**Database Schema:**
{schema}

### Example 

**Schema:**
Table: customers
- customer_id (int)
- name (varchar)
- email (varchar)
- city (varchar)

Table: orders
- order_id (int)
- customer_id (int)
- order_date (date)
- total_amount (decimal)


**Natural Language Request:**
> Get the names and emails of customers who placed orders over $500 after January 1, 2023.
**LLM Output:**
sql
SELECT c.name, c.email
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
WHERE o.total_amount > 500
AND o.order_date > '2023-01-01';
        """,
        tools=[get_current_time],
        output_type=SQLResponse,
        temperature=1,
    )

    return agent


def create_extract_agent() -> Agent:
    """
    Create an agent that extracts information from the text based on the provided schema.
    """
    schema = open("dbschema.txt", "r").read()
    extract_agent = Agent(
        system_prompt=f"""

        # SQL Intent Extraction Prompt

        ## Task Description
        You are an AI assistant specialized in understanding user queries about database operations. Your task is to extract two pieces of information from each user query with taking into account the previous conversation history:

        1. **Action**: Must be one of: `read`, `write`, `update`, or `delete`
        2. **Resource**: Must be a valid table name from the database schema provided below

        ## Available Database Schema
        
        {schema}
        

        ## Action Definitions
        - **read**: Any query asking to retrieve, view, get, show, find, search, list, or display data
        - **write**: Any query asking to insert, add, create, or put new data
        - **update**: Any query asking to modify, change, alter, edit, or revise existing data
        - **delete**: Any query asking to remove, drop, eliminate, or destroy data

        ## Instructions
        1. Analyze the user query in context of any previous conversation history
        2. Identify the intended database action (read, write, update, or delete)
        3. Identify the target database table (must be one of the tables in the provided schema)
        4. Format your response as a JSON object with two fields: `action` and `resource`
        5. If multiple actions or resources are mentioned, prioritize the primary intent
        6. If no valid action or resource can be identified, return `null` for the respective field

        If there is any irrelevant information in the user query, return the response accordingly.
        """,
        model=model,
        output_type=ExtractResponse,
    )
    return extract_agent
