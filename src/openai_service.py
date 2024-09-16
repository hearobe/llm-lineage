import json5
from pydantic import BaseModel
from openai import OpenAI
client = OpenAI()

class SourceTableAndColumn(BaseModel):
    source_table: str
    column: str

class ColumnLineageResponse(BaseModel):
    column: str
    lineage: list[SourceTableAndColumn]

class ChatSession:
    def __init__(self, model_name: str, model: str):
        self.model = model
        self.model_name = model_name
        self.messages = [
            {
                "role": "system",
                "content": 
                    f"""You are a data analyst who is teaching someone how to trace the column lineage of a dbt SQL model.
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
                    
                    Only return JSON. Do not return any plaintext or formatting.
                    
                    model name: {model_name}

                    model code:
                    {model}"""
            }
        ]
    
    def get_column_lineage(self, column:str):
        self.messages.append({
                "role": "user",
                "content": f"get lineage of {column}"
            })
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=self.messages,
            # response_format=ColumnLineageResponse,
            temperature=1,
            max_tokens=2048,
            top_p=1,
            frequency_penalty=0.2,
        )

        print(f"""resut from get_column_lineage:
              {completion.choices[0].message.content}""")

        return json5.loads(completion.choices[0].message.content)

    
    def get_corrected_column_lineage(self, incorrect_sources: list):
        self.messages.append({
                "role": "user",
                "content": f"""{incorrect_sources}
                
                These do not seem like the right source tables or columns. Can you find the sources of these intermediate tables or columns?"""
            })
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=self.messages,
            # response_format=ColumnLineageResponse,
            temperature=1,
            max_tokens=2048,
            top_p=1,
            frequency_penalty=0.2,
        )

        print(f"""resut from get_corrected_column_lineage:
              {completion.choices[0].message.content}""")

        return json5.loads(completion.choices[0].message.content)
