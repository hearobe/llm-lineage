from pathlib import Path

import json5
from api_methods import initiate_lineage_trace
from db_repository import DBRepository
from model_parser import ModelParser
from schema_parser import SchemaParser

# file = Path('repo/dbt/models/marts/schools/dim_schools.sql')


# schemaParser = SchemaParser()
# for file in schema_files:
#     schemaParser.parseModels(file)



def manual_testing():
    db = DBRepository()
    result = db.get_status()
    print(result)
    # print(result[0]["transformation_summary"])


manual_testing()
