import os
import yaml
from pathlib import Path
from neo4j import GraphDatabase
import google.generativeai as genai
from openai import OpenAI

def get_initial_prompt(column: str):
    return f"""
Determine the source columns and source tables or CTEs that the output column {column} directly derives from.
Only return the columns from tables or CTEs specified in the from clause of the output query. Only consider columns specified in the Select clause.
Return your results in the following yaml format. Do not include content other than the yaml, and return the contents in plaintext without formatting,
and make sure there are no duplicates

- name: source_cte_name
  source_columns:
    - name: column_name_1
    - name: column_name_2
"""

def get_intermediate_prompt(column:str, cte:str):
    return f"""
Determine the source columns and source tables or CTEs that the column {column} in CTE {cte} directly derives from.
Direct derivation only applies to the tables or CTEs specified in the {cte} CTE. Only consider columns specified in the Select clause.
Return your results in the following yaml format. Do not include content other than the yaml, return the contents in plaintext without formatting.
and make sure there are no duplicates

- name: source_cte_name
  source_columns:
    - name: column_name_1
    - name: column_name_2
"""

def handle_prompt_response(response:str, intermediate_columns: list, output_column: str, output_table: str):
    print(response)
    source_tables_or_ctes = yaml.safe_load(response)
    print(source_tables_or_ctes)
    
    for source_table_or_cte in source_tables_or_ctes:
        source_table_db, _, _ = driver.execute_query(
            """MATCH (t:Table {name: $table_name})
                RETURN t""",
            table_name=source_table_or_cte["name"],
            database_="neo4j",
        )
        if source_table_db is None or len(source_table_db) == 0:
            print("Adding to intermediate_columns")
            for column in source_table_or_cte["source_columns"]:
                intermediate_column = {"cte": source_table_or_cte["name"], "column": column["name"]}
                if intermediate_column not in intermediate_columns:
                    intermediate_columns.append(intermediate_column)
            print(intermediate_columns)
        else:
            print("source table reached")
            for source_column in source_table_or_cte["source_columns"]:
                source_column_db, _, _ = driver.execute_query(
                    """MATCH (t:Table {name: $table_name})-[:HAS_COLUMN]->(c:Column  {name: $column_name})
                        RETURN c""",
                    table_name=source_table_or_cte["name"],
                    column_name=source_column["name"],
                    database_="neo4j",
                )
                print(source_column_db)
                if source_column_db is None or len(source_column_db) < 1:
                    raise Exception("Source column does not exist in source table")
                else:
                    transformation_summary = model.generate_content(query + "\n" + 
                                                f"""Describe in 1-2 sentences what transformations were done to transform 
                                                the source column {source_column["name"]} in {source_table_or_cte["name"]} 
                                                to the output column {output_column} in {output_table}""")
                    summary = driver.execute_query(
                        """MATCH (source_column:Column {name: $source_column})-[:IS_COLUMN_IN]->(t:Table {name: $source_table})
                            MATCH (output_column:Column {name: $output_column})-[:IS_COLUMN_IN]->(t:Table {name: $output_table})
                            CREATE (source_column)-[:IS_USED_BY {transformation_summary: $transformation_summary}]->(output_column)
                            CREATE (output_column)-[:IS_DERIVED_FROM {transformation_summary: $transformation_summary}]->(source_column)""",
                        source_column = source_column["name"],
                        output_column = output_column,
                        source_table=source_table_or_cte["name"],
                        output_table=output_table,
                        transformation_summary = transformation_summary.text,
                        database_="neo4j",
                    ).summary
                    print(summary.counters.relationships_created)

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")

URI = "neo4j://neo4j"
AUTH = ("neo4j", os.environ["NEO4J_PASSWORD"])

with GraphDatabase.driver(URI, auth=AUTH) as driver:
    driver.verify_connectivity()
    print("Connection established.")

dirname = os.path.dirname(__file__)
path = os.path.join(dirname, '../data/dim_district_status.sql')

# Verify the SQL model exists in the schema
records, summary, keys = driver.execute_query(
    """MATCH (t:Table {name: $table_name})
        RETURN t""",
    table_name="dim_district_status",
    database_="neo4j",
)
if records is None or len(records) == 0:
    raise Exception("Please specify all models in a yml file.")
if len(records) > 1:
    raise Exception("Tables should have unique names")

print(records)

# Retrieve output columns of the table
records, summary, keys = driver.execute_query(
    """MATCH (t:Table {name: $table_name})-[:HAS_COLUMN]->(c:Column)
        RETURN c.name AS column_name""",
    table_name="dim_district_status",
    database_="neo4j",
)
if records is None or len(records) == 0:
    raise Exception("Please specify all columns of the model in a yml file.")

print(records)
print(records[0]['column_name'])

full_query = Path(path).read_text()

# Remove formatting whitespace to reduce token count
query = " ".join(full_query.split())

# LLM querying for each column
intermediate_columns = []
for record in records:
    output_column = record["column_name"]
    response = model.generate_content(query + "\n\n" + get_initial_prompt(output_column))
    handle_prompt_response(response.text, intermediate_columns, output_column, "dim_district_status")
    print(intermediate_columns)

    while len(intermediate_columns) > 0:
        current_column = intermediate_columns.pop()
        print(current_column)
        print(get_intermediate_prompt(current_column['column'], current_column['cte']))
        response = model.generate_content(query + "\n\n" + get_intermediate_prompt(current_column['column'], current_column['cte']))
        handle_prompt_response(response.text, intermediate_columns, output_column, "dim_district_status")

    

# response = model.generate_content(query + "\n\n" + get_initial_prompt('school_district_id'))
# print(response.text)
