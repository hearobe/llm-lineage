from pathlib import Path
from typing import List

from db_service import DBService
from openai_service import ChatSession, SourceTableAndColumn

class ModelParser:
    def parseFile(self, filepath: Path):
        db = DBService()

        model_name = filepath.stem
        output_model_record = db.find_one_table(model_name)
        if output_model_record == None or len(output_model_record) == 0:
            print(f"Model {model_name} not found")
        
        # TODO: use prod version of the function after testing is done
        output_column_records = db.find_columns_of_table_dev(model_name)
        if output_column_records == None or len(output_column_records) == 0:
            return
        output_columns = [x["name"] for x in output_column_records]

        # output_columns = ['school_district_id']

        print(f"parsing {model_name} for columns {output_columns}")

        full_query = Path(filepath).read_text()

        # Remove formatting whitespace to reduce token count
        query = " ".join(full_query.split())

        llm = ChatSession(model_name, query)
        # schema = db.get_source_table_schema(llm.get_source_table_names)
        # llm.set_schema(schema)

        for output_column in output_columns:
            sources: List[SourceTableAndColumn] | None = llm.get_column_lineage(output_column)
            if sources is None:
                continue

            validated_sources: List[SourceTableAndColumn] = []
            unvalidated_sources: List[SourceTableAndColumn] = sources or []
            incorrect_sources: List[SourceTableAndColumn] = []
            retry_limit = 4
            while retry_limit > 0:
                if retry_limit < 4:
                    print(f'try number: {4-retry_limit}')
                    print(unvalidated_sources)
                for element in unvalidated_sources:
                    if db.is_valid_source(table_name=element.source_table, column_name=element.column):
                        validated_sources.append(element)
                    else:
                        # print("source table not found")
                        incorrect_sources.append(element)

                if len(incorrect_sources) == 0:
                    break

                retry_limit -= 1
                unvalidated_sources = llm.get_corrected_column_lineage(incorrect_sources)
                incorrect_sources = []

            print("----------------validation completed----------------")
            print(validated_sources)

            for source in validated_sources:
                db.create_column_lineage_relationships(
                    source_column=source.column,
                    source_table=source.source_table,
                    output_column=output_column,
                    output_table=model_name,
                    transformation_summary=source.transformation_summary,
                )


