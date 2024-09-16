import os
import json
from pathlib import Path
from neo4j import GraphDatabase
from db_service import DBService
from openai_service import ChatSession

db = DBService()

dirname = os.path.dirname(__file__)
path = os.path.join(dirname, '../data/dim_district_status.sql')

# # Verify the SQL model exists in the schema
# output_table = db.find_one_table("dim_district_status")
# print(output_table)

# # Retrieve output columns of the table
# output_columns = db.find_columns_of_table("dim_district_status")
# print(output_columns)

output_columns = [
    {
        "name": "status"
    },
    {
        "name": "school_year"
    },
    {
        "name": "school_district_id"
    }
]

full_query = Path(path).read_text()

# Remove formatting whitespace to reduce token count
query = " ".join(full_query.split())

llm = ChatSession("dim_district_status", query)
db = DBService()

for output_column in output_columns:
    print(output_column)
    sources = llm.get_column_lineage(output_column["name"])


    # response = """
    # {
    #     "column": "status",                                                                                                                
    #     "lineage": [                                                                                                                         
    #         {                                                                                                                                
    #             "source_table": "int_active_sections",
    #             "column": "course_name",
    #             "transformation_summary": "No transformations done"                                                                                     
    #         },
    #         {
    #             "source_table": "dim_schools",
    #             "column": "school_id",
    #             "transformation_summary": "No transformations done"   
    #         }                                                                                                                                
    #     ]                                                                                                                                    
    # }"""


    validated_sources = []
    unvalidated_sources = sources["lineage"]
    incorrect_sources = []
    retry_limit = 10
    while retry_limit > 0:
        for element in unvalidated_sources:
            if db.is_valid_source(table_name=element["source_table"], column_name=element["column"]):
                validated_sources.append(element)
            else:
                print("source table not found")
                incorrect_sources.append(element)
        
        # print(f"try {10-retry_limit} valid")
        # print(validated_sources)
        # print(f"try {10-retry_limit} incorrect")
        # print(incorrect_sources)

        if len(incorrect_sources) == 0:
            break

        retry_limit -= 1
        unvalidated_sources = llm.get_corrected_column_lineage(incorrect_sources)["lineage"]
        # print("response from get_corrected_column_lineage")
        # print(unvalidated_sources)
        # print(type(unvalidated_sources))
        incorrect_sources = []

    print("----------------validation completed----------------")
    print(validated_sources)
    # print(incorrect_sources)
    # print(unvalidated_sources)


    for source in validated_sources:
        db.create_column_lineage_relationships(
            source_column=source["column"],
            source_table=source["source_table"],
            output_column=output_column["name"],
            output_table="dim_district_status",
            transformation_summary=source["transformation_summary"],
        )


db.close()
