from typing import List
import json5
from pydantic import BaseModel
from openai import OpenAI

from db_service import DBService
client = OpenAI()

class SourceTableAndColumn(BaseModel):
    source_table: str
    column: str
    transformation_summary: str

class ColumnLineageResponse(BaseModel):
    column: str
    lineage: list[SourceTableAndColumn]

class ChatSession:
    def __init__(self, model_name: str, model: str):
        self.model = model
        self.model_name = model_name

        db = DBService()
        self.schema = db.get_source_table_schema(self.get_source_table_names())

        self.messages = [
            {
                "role": "system",
                "content": 
                    f"""You are a data analyst who is teaching someone how to trace the column lineage of a dbt SQL model with the help of the source table schema.
                    Given a column from the output model, find the column(s) and source table(s) that the given column directly
                    derives from. Intermediate CTEs cannot be considered source tables. Walk through how you trace through the code.
                    After thinking about it, return only the source tables and columns. For each source column,
                    include a one-liner summarizing the transformations done to derive the output data from source data.
                    If no transformations were done, the summary should be “No transformation done”.
                    Please return these in a JSON format that looks something like the following:

                    {{
                        "column": "output_column_name",
                        "lineage": [{{
                            "source_table": "table_name",
                            "column": "table_column_name",
                            "transformation_summary": "description of transformations done"
                        }}, {{...}}]
                    }}
                    
                    Only return a single JSON object. Do not return any plaintext or formatting.

                    schema: {self.schema}
                    
                    model name: {model_name}

                    model code:
                    {model}"""
            }
        ]

    def get_source_table_names(self):
        self.messages = [
            {
                "role": "system",
                "content": 
                    f"""You are a data analyst who wants to find the source tables given an SQL query. Return the source tables as a single JSON object that looks like the following, without any plaintext or formatting.
                        {{
                            "source_tables": ["table_name_1", "table_name_2", ...]
                        }}"""
            }, 
            {
                "role": "user",
                "content": f"{self.model}"
            }
        ]

        completion = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=self.messages,
            temperature=1,
            max_tokens=2048,
            top_p=1,
            frequency_penalty=0.2,
        )

        return json5.loads(completion.choices[0].message.content)["source_tables"]
    
    def get_column_lineage(self, column:str) -> List[SourceTableAndColumn] | None:
        self.messages.append({
                "role": "user",
                "content": f"get lineage of {column}"
            })
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=self.messages,
            temperature=1,
            max_tokens=2048,
            top_p=1,
            frequency_penalty=0.2,
        )

        return self.get_parsed_response(completion.choices[0].message.content)

    def get_corrected_column_lineage(self, incorrect_sources: list) -> List[SourceTableAndColumn] | None:
        self.messages.append({
                "role": "user",
                "content": f"""{incorrect_sources}
                
                These do not seem like the right source tables or columns. Can you try again?"""
            })
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=self.messages,
            temperature=1,
            max_tokens=2048,
            top_p=1,
            frequency_penalty=0.2,
        )

        return self.get_parsed_response(completion.choices[0].message.content)
    
    def get_parsed_response(self, unformatted: str):
        try:
            response = ColumnLineageResponse(**json5.loads(unformatted))
            return response.lineage
        except:
            self.messages.append({
                "role": "user",
                "content": f"""{unformatted}
                
                Formatting here is incorrect. Please make sure this is a valid JSON format that looks something like the following. Only one JSON object should be returned.

                    {{
                        "column": "output_column_name",
                        "lineage": [{{
                            "source_table": "table_name",
                            "column": "table_column_name",
                            "transformation_summary": "description of transformations done"
                        }}, {{...}}]
                    }}
                """
            })
            completion = client.beta.chat.completions.parse(
                model="gpt-4o-mini",
                messages=self.messages,
                temperature=1,
                max_tokens=2048,
                top_p=1,
                frequency_penalty=0.2,
            )
            try:
                response = ColumnLineageResponse(**json5.loads(completion.choices[0].message.content))
                return response.lineage
            except:
                return None

