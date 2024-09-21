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
    
    def set_status(self, status: str):
        status_record, _, _ = self.driver.execute_query(
            """MERGE (s:LineageTraceStatus {name: $name})
                SET s.status = $status
                RETURN s.status as status""",
            name='status',
            status=status,
            database_=self.database_,
        )
        return status_record[0]["status"]
    
    def get_status(self):
        status_record, _, _ = self.driver.execute_query(
            """MATCH (s:LineageTraceStatus {name: $name})
                RETURN s.status as status""",
            name='status',
            database_=self.database_,
        )
        if status_record is None or len(status_record) == 0:
            return self.set_status('static')
        else:
            return status_record[0]["status"]
    
    def find_one_table(self, table_name: str):
        output_table, _, _ = self.driver.execute_query(
            """MATCH (t:Table {name: $table_name})
                RETURN t""",
            table_name=table_name,
            database_=self.database_,
        )
        
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
    
    def find_columns_of_table_dev(self, table_name: str):
        output_columns, _, _ = self.driver.execute_query(
            """MATCH (t:Table {name: $table_name})-[:HAS_COLUMN]->(c:Column)
                WHERE NOT (c)-[:IS_DERIVED_FROM]->(:Column)
                RETURN c.name as name""",
            table_name=table_name,
            database_=self.database_,
        )
        
        return output_columns
    
    def create_table(self, table_name: str):
        self.driver.execute_query(
            """MERGE (:Table {name: $name})""",
            name=table_name,
            database_=self.database_,
        )

    def create_column_in_table(self, column_name: str, table_name: str):
        self.driver.execute_query(
            """MATCH (t:Table {name: $table_name}) 
                MERGE (c:Column {name: $column_name, table_name: $table_name}) 
                MERGE (t)-[:HAS_COLUMN]->(c)
                MERGE (c)-[:IS_COLUMN_IN]->(t)""",
            table_name = table_name,
            column_name = column_name,
            database_=self.database_,
        )
    
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
        print(f"entered create_column_lineage_relationships with source ({source_table}, {source_column}) and output ({output_table}, {output_column})")
        summary = self.driver.execute_query(
            """MATCH (source_column:Column {name: $source_column, table_name: $source_table})
                MATCH (output_column:Column {name: $output_column, table_name: $output_table})
                MERGE (source_column)-[:IS_USED_BY {transformation_summary: $transformation_summary}]->(output_column)
                MERGE (output_column)-[:IS_DERIVED_FROM {transformation_summary: $transformation_summary}]->(source_column)""",
            source_column=source_column,
            source_table=source_table,
            output_column=output_column,
            output_table=output_table,
            transformation_summary = transformation_summary,
            database_=self.database_,
        ).summary

        print("{summary.counters.relationships_created} relationships created between source ({source_table}, {source_column}) and output ({output_table}, {output_column})")

    def close(self):
        self.driver.close()
