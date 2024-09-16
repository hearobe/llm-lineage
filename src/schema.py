import yaml
import os

from neo4j import GraphDatabase

URI = "neo4j://neo4j"
AUTH = ("neo4j", "password")

with GraphDatabase.driver(URI, auth=AUTH) as driver:
    driver.verify_connectivity()
    print("Connection established.")

dirname = f"{os.path.dirname(__file__)}/{os.pardir}/data"

# List to store YAML file names
yaml_files = []

# Loop through all files in the directory
for filename in os.listdir(dirname):
    print(filename)
    # Check if the file ends with .yaml or .yml
    if filename.endswith('.yaml') or filename.endswith('.yml'):
        yaml_files.append(filename)

for file in yaml_files:
    path = os.path.join(dirname, file)
    print(path)

    file = open(path)
    print(file)
    district_models = yaml.safe_load(file)

    if "models" in district_models:
        for model in district_models["models"]:
            if "name" not in model or "columns" not in model:
                raise Exception(f"Invalid model resource in {path}")
            
            table_name = model["name"]

            existing_table, _, _ = driver.execute_query(
                """MATCH (t:Table {name: $table_name})
                    RETURN t""",
                table_name=table_name,
                database="neo4j"
            )
            if existing_table is not None and len(existing_table) > 0:
                print(f"{table_name} already exists, skipping creation")
                continue

            print("Populating schema for " + table_name)

            # Create table node
            summary = driver.execute_query(
                """CREATE (:Table {name: $name})""",
                name=table_name,
                database_="neo4j",
            ).summary
            print("Created {nodes_created} nodes in {time} ms.".format(
                nodes_created=summary.counters.nodes_created,
                time=summary.result_available_after
            ))

            for column in model["columns"]:
                print("Adding " + column["name"] + " to " + table_name)

                # Create column node and bidirectional relationship between table and column
                summary = driver.execute_query(
                    """MATCH (t:Table {name: $table_name}) 
                        CREATE (c:Column {name: $column_name, table_name: $table_name}) 
                        CREATE (t)-[:HAS_COLUMN]->(c)
                        CREATE (c)-[:IS_COLUMN_IN]->(t)""",
                    table_name = table_name,
                    column_name = column["name"],
                    database_="neo4j",
                ).summary
                print("Created {nodes_created} nodes in {time} ms.".format(
                    nodes_created=summary.counters.nodes_created,
                    time=summary.result_available_after
                ))
