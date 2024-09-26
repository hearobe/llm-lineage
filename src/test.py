from pathlib import Path

import json5
from api_methods import initiate_lineage_trace
from db_service import DBService
from model_parser import ModelParser
from schema_parser import SchemaParser

# file = Path('repo/dbt/models/marts/schools/dim_schools.sql')


# schemaParser = SchemaParser()
# for file in schema_files:
#     schemaParser.parseModels(file)



def manual_testing():
    db = DBService()
    result = db.get_lineage(column_name='district_frl_eligible_percent', table_name='dim_districts')
    print(result)
    # print(result[0]["transformation_summary"])


manual_testing()
