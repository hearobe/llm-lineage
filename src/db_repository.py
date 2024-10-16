import os
from neo4j import GraphDatabase

class DBRepository:
    def __init__(self):
        URI = "neo4j://neo4j"
        # URI = "neo4j://localhost"
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
    
    def find_columns_of_table_old(self, table_name: str):
        output_columns, _, _ = self.driver.execute_query(
            """MATCH (t:Table {name: $table_name})-[:HAS_COLUMN]->(c:Column)
                RETURN c.name as name""",
            table_name=table_name,
            database_=self.database_,
        )
        if output_columns is None or len(output_columns) == 0:
            raise Exception("Columns could not be found")
        
        return output_columns
    
    def find_columns_of_table(self, table_name: str):
        output_columns, _, _ = self.driver.execute_query(
            """MATCH (t:Table {name: $table_name})-[:HAS_COLUMN]->(c:Column)
                WHERE NOT (c)-[:IS_DERIVED_FROM]->(:Column)
                RETURN c.name as name""",
            table_name=table_name,
            database_=self.database_,
        )
        
        return output_columns
    
    def find_column_in_table(self, column_name: str, table_name: str):
        column, _, _ = self.driver.execute_query(
            """MATCH (c:Column {name: $column_name, table_name: $table_name}) 
                RETURN c""",
            table_name = table_name,
            column_name = column_name,
            database_=self.database_,
        )
        print(column)

        return column
    
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
    
    def create_column_lineage_relationships(self, source_table: str, source_column: str, output_table: str, output_column: str, transformation_summary: str):
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

        print(f"{summary.counters.relationships_created} relationships created between source ({source_table}, {source_column}) and output ({output_table}, {output_column})")

    def get_source_table_schema(self, source_tables: list[str]):
        result = {}
        for source_table in source_tables:
            column_records, _, _ = self.driver.execute_query(
                """MATCH (c:Column {table_name: $source_table})
                    RETURN c.name as name""",
                source_table=source_table,
                database_=self.database_,
            )
            columns = []
            for record in column_records:
                columns.append(record["name"])
            result[source_table] = columns
        
        return result
    
    def get_lineage(self, column_name: str, table_name: str, downstream_only: bool = False, upstream_only: bool = False):
        if downstream_only and upstream_only:
            print("downstream_only and upstream_only cannot both be true")
            return None

        downstream_nodes = self.get_downstream_lineage_nodes(column_name=column_name, table_name=table_name) if not downstream_only else []
        upstream_nodes = self.get_upstream_lineage_nodes(column_name=column_name, table_name=table_name) if not upstream_only else []
        downstream_edges = self.get_downstream_lineage_edges(column_name=column_name, table_name=table_name) if not downstream_only else []
        upstream_edges = self.get_upstream_lineage_edges(column_name=column_name, table_name=table_name) if not upstream_only else []

        nodes = [
            {
                "id": node["column_id"],
                "columnName": node["column_name"],
                "tableName": node["table_name"]
            }
            for node in downstream_nodes
        ] + [
            {
                "id": f"{table_name}|{column_name}",
                "columnName": column_name,
                "tableName": table_name
            }
        ] + [
            {
                "id": node["column_id"],
                "columnName": node["column_name"],
                "tableName": node["table_name"]
            }
            for node in upstream_nodes
        ]
        edges = [
            {
                "startId": edge["start_id"],
                "startColumnName": edge["start_column_name"],
                "startTableName": edge["start_table_name"],
                "endId": edge["end_id"],
                "endColumnName": edge["end_column_name"],
                "endTableName": edge["end_table_name"],
                "transformationSummary": edge["transformation_summary"]
            }
            for edge in downstream_edges + upstream_edges
        ]
        result = {
            "nodes": nodes,
            "edges": edges
        }
        return result

    
    def get_downstream_lineage_nodes(self, column_name: str, table_name: str):
        records, _, _ = self.driver.execute_query(
            f"""MATCH (c:Column {{name: $name, table_name: $table_name}})
                MATCH (related_column:Column)-[r:IS_USED_BY*1..10]->(c)
                WITH DISTINCT related_column
                RETURN 
                related_column.table_name + '|' + related_column.name AS column_id,
                related_column.name AS column_name,
                related_column.table_name AS table_name
                """,
                name=column_name,
                table_name=table_name,
                database_=self.database_,
        )
        return records
    
    def get_downstream_lineage_edges(self, column_name: str, table_name: str):
        records, _, _ = self.driver.execute_query(
            """MATCH (c:Column {name: $name, table_name: $table_name})
                MATCH (related_column:Column)-[r:IS_USED_BY*1..10]->(c)
                UNWIND r as rel
                WITH DISTINCT rel, startNode(rel) AS startNode, endNode(rel) AS endNode
                RETURN 
                startNode.table_name + '|' + startNode.name AS start_id,
                startNode.name AS start_column_name,
                startNode.table_name AS start_table_name,
                endNode.table_name + '|' + endNode.name AS end_id,
                endNode.name AS end_column_name,
                endNode.table_name AS end_table_name,
                rel.transformation_summary AS transformation_summary
                """,
                name=column_name,
                table_name=table_name,
                database_=self.database_,
        )
        return records
    
    def get_upstream_lineage_nodes(self, column_name: str, table_name: str):
        records, _, _ = self.driver.execute_query(
            f"""MATCH (c:Column {{name: $name, table_name: $table_name}})
                MATCH (c)-[r:IS_USED_BY*1..10]->(related_column:Column)
                WITH DISTINCT related_column
                RETURN 
                related_column.table_name + '|' + related_column.name AS column_id,
                related_column.name AS column_name,
                related_column.table_name AS table_name
                """,
                name=column_name,
                table_name=table_name,
                database_=self.database_,
        )
        return records
    
    def get_upstream_lineage_edges(self, column_name: str, table_name: str):
        records, _, _ = self.driver.execute_query(
            """MATCH (c:Column {name: $name, table_name: $table_name})
                MATCH (c)-[r:IS_USED_BY*1..10]->(related_column:Column)
                UNWIND r as rel
                WITH DISTINCT rel, startNode(rel) AS startNode, endNode(rel) AS endNode
                RETURN 
                startNode.table_name + '|' + startNode.name AS start_id,
                startNode.name AS start_column_name,
                startNode.table_name AS start_table_name,
                endNode.table_name + '|' + endNode.name AS end_id,
                endNode.name AS end_column_name,
                endNode.table_name AS end_table_name,
                rel.transformation_summary AS transformation_summary
                """,
                name=column_name,
                table_name=table_name,
                database_=self.database_,
        )
        return records

    def close(self):
        self.driver.close()
