import os
from neo4j import GraphDatabase


class DBService:
    def __init__(self):
        URI = "neo4j://neo4j"
        AUTH = ("neo4j", os.environ["NEO4J_PASSWORD"])
        self.driver = GraphDatabase.driver(URI, auth=AUTH)
        self.database_ = "neo4j"

        try:
            self.driver.verify_connectivity()
            print("Connection established.")
        except Exception as e:
            print(f"An error occurred while connecting to database: {e}")
    
    def find_one_table(self, table_name: str):
        output_table, _, _ = self.driver.execute_query(
            """MATCH (t:Table {name: $table_name})
                RETURN t""",
            table_name=table_name,
            database_=self.database_,
        )
        if output_table is None or len(output_table) == 0:
            raise Exception("Table could not be found")
        
        return output_table
    
    def find_columns_of_table(self, table_name: str):
        output_columns, _, _ = self.driver.execute_query(
            """MATCH (t:Table {name: $table_name})-[:HAS_COLUMN]->(c:Column)
                RETURN c.name as name""",
            table_name=table_name,
            database_=self.database_,
        )
        if output_columns is None or len(output_columns) == 0:
            raise Exception("Columns could not be found")
        
        return output_columns
    
    def is_valid_source(self, table_name: str, column_name: str):
        source, _, _ = self.driver.execute_query(
            """MATCH (t:Table {name: $table_name})-[:HAS_COLUMN]->(c:Column  {name: $column_name})
                RETURN t""",
            table_name=table_name,
            column_name=column_name,
            database_=self.database_,
        )

        if source is None or len(source) <= 0:
            return False
        return True
    
    # TODO: prevent duplicates: if the relationship already exists, update it with transformation summary
    def create_column_lineage_relationships(self, source_table: str, source_column: str, output_table: str, output_column: str, transformation_summary: str):
        summary = self.driver.execute_query(
            """MATCH (source_column:Column {name: $source_column, table_name: $source_table})
                MATCH (output_column:Column {name: $output_column, table_name: $output_table})
                CREATE (source_column)-[:IS_USED_BY {transformation_summary: $transformation_summary}]->(output_column)
                CREATE (output_column)-[:IS_DERIVED_FROM {transformation_summary: $transformation_summary}]->(source_column)""",
            source_column=source_column,
            source_table=source_table,
            output_column=output_column,
            output_table=output_table,
            transformation_summary = transformation_summary,
            database_=self.database_,
        ).summary
        
        if summary.counters.relationships_created != 2:
            raise Exception(f"""Only {summary.counters.relationships_created} relationships created for column {source_column} in table {source_table}""")
    
    def is_valid_source_mock(self, source: object):
        source_tables = ["dim_districts", "dim_district_status", "stg_external_datasets__districts_enrolled", "int_school_years", "dim_schools", "int_teacher_schools_historical", "int_active_sections"]
        return source["source_table"] in source_tables

    def close(self):
        self.driver.close()
