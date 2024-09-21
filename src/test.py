# import os
import json5
# from neo4j import GraphDatabase

from db_service import DBService
from openai_service import ColumnLineageResponse

db = DBService()
print(db.get_status())

# db.init_database()
db.set_status("in_progress")
print(db.get_status())







#  FILE DIRECTORY DISCOVERY AND TRAVERSAL
# yaml_files = []
# # dirname = os.path.dirname("c:/Users/tanyl/llm-lineage/data/dim_district_status")
# print(os.path.dirname(__file__))
# print(os.path.realpath)
# print(os.pardir)
# dirname = os.chdir(f"{os.path.dirname(__file__)}/{os.pardir}/data")
# print(dirname)

# # Loop through all files in the directory
# for filename in os.listdir(dirname):
#     # Check if the file ends with .yaml or .yml
#     if filename.endswith('.yaml') or filename.endswith('.yml'):
#         yaml_files.append(filename)

# print(yaml_files)


