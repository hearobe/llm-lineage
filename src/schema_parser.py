import yaml
from pathlib import Path

from db_repository import DBRepository

class SchemaParser:
    def parseModels(self, filepath: Path):
        fileContents = yaml.safe_load(open(filepath))

        # Validate that model schema exists
        if "models" not in fileContents:
            print(f"File {filepath.name} does not contain model schema. Skipping.")
            return None
        
        db = DBRepository()
        
        for model in fileContents["models"]:
            # Validate that columns of model exists
            if "name" not in model or "columns" not in model:
                raise Exception(f"Invalid model resource in {filepath.name}")
            
            table_name = model["name"]

            ## To speed up testing
            # existing_table_records = db.find_one_table(table_name)
            # if existing_table_records is not None and len(existing_table_records) > 0:
            #     print(f"{table_name} already exists, skipping creation")
            #     continue

            print("Populating schema for " + table_name)

            # Create table node
            db.create_table(table_name)

            for column in model["columns"]:
                print("Adding " + column["name"] + " to " + table_name)

                # Create column node and bidirectional relationship between table and column
                db.create_column_in_table(table_name=table_name, column_name=column["name"])

        db.close()
