from fastapi import HTTPException
from db_repository import DBRepository
from filesystem_repository import FilesystemRepository
from model_parser import ModelParser
from schema_parser import SchemaParser

def validate_lineage_trace():
    db = DBRepository()

    # exit if there is an ongoing trace
    if db.get_status() == "in_progress":
        raise HTTPException(
            status_code=409, 
            detail="Cannot initiate another lineage trace while lineage trace is in progress"
        )

def initiate_lineage_trace():
    db = DBRepository()
    
    # set status
    db.set_status("in_progress")

    # Get schema and model files
    fs = FilesystemRepository()
    schema_files, model_files = fs.get_schema_and_model_files()

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

    db = DBRepository()
    if db.get_status() == "in_progress":
        raise HTTPException(status_code=409, detail="Cannot get lineage while lineage trace is in progress")
    if len(db.find_column_in_table(column_name, table_name)) == 0:
        raise HTTPException(status_code=404, detail="Column does not exist")
    lineage = db.get_lineage(column_name, table_name, downstream_only, upstream_only)
    db.close()
    return lineage
