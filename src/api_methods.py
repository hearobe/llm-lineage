from db_service import DBService
from file_service import FileService
from model_parser import ModelParser
from schema_parser import SchemaParser

def initiate_lineage_trace():
    # set status
    db = DBService()
    db.set_status("in_progress")

    # iterate through the repo
    ## find dbt_project.yml. retrieve the model paths specified. 
    ## for each model path,
    ## traverse all files and subdirectories in model path
    ## push all yml files into an array of schema files, and all sql files into an array of model files
    fs = FileService()
    schema_files, model_files = fs.get_schema_and_model_files()

    # print(schema_files)
    # print(model_files)

    # PARSE SCHEMA
    # for each yml file
    # skip if there is no 'models' property
    # run code in schema.py from line 26 onwards
    schemaParser = SchemaParser()
    for file in schema_files:
        schemaParser.parseModels(file)

    # PARSE SQL
    # for each sql file
    # run the code in sql-parser
    sqlParser = ModelParser()
    for file in model_files:
        sqlParser.parseFile(file)

    db.set_status('static')
    print(db.get_status())

    # wind down
    db.close()

def get_lineage_of_column(column_name: str, table_name: str, downstream_only: bool = False, upstream_only: bool = False):
    if downstream_only and upstream_only:
        print("downstream_only and upstream_only cannot both be true")
        return None

    db = DBService()
    lineage = db.get_lineage(column_name, table_name, downstream_only, upstream_only)
    db.close()
    return lineage
