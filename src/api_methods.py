from db_service import DBService
from file_service import FileService
from model_parser import ModelParser
from schema_parser import SchemaParser

def initiate_lineage_trace():
    print("huhh???")
    # set status
    db = DBService()
    # db.init_database()
    db.set_status("in_progress")
    print(db.get_status())

    # status = db.get_status()
    # print(f"status: {status}")

    # # iterate through the repo
    # ## find dbt_project.yml. retrieve the model paths specified. 
    # ## for each model path,
    # ## traverse all files and subdirectories in model path
    # ## push all yml files into an array of schema files, and all sql files into an array of model files
    # fs = FileService()
    # schema_files, model_files = fs.get_schema_and_model_files()

    # print(schema_files)
    # print(model_files)

    # # PARSE SCHEMA
    # # for each yml file
    # # skip if there is no 'models' property
    # # run code in schema.py from line 26 onwards
    # schemaParser = SchemaParser()
    # for file in schema_files:
    #     schemaParser.parseModels(file)

    # # PARSE SQL
    # # for each sql file
    # # run the code in sql-parser
    # sqlParser = ModelParser()
    # for file in model_files:
    #     sqlParser.parseFile(file)

    db.set_status('static')
    print(db.get_status())

    # wind down
    db.close()
