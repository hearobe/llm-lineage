from pathlib import Path
from typing import List

from db_repository import DBRepository
from openai_repository import LLMRepository, SourceTableAndColumn

class ModelParser:
    def parseFile(self, filepath: Path):
        db = DBRepository()

        model_name = filepath.stem
        output_model_record = db.find_one_table(model_name)
        if output_model_record == None or len(output_model_record) == 0:
            print(f"Model {model_name} not found")

        full_query = Path(filepath).read_text()

        # Remove formatting whitespace
        query = " ".join(full_query.split())

        llm = LLMRepository(model_name, query)

        output_column_records = db.find_columns_of_table(model_name)
        if output_column_records == None or len(output_column_records) == 0:
            return
        output_columns = [x["name"] for x in output_column_records]

        print(f"parsing {model_name} for columns {output_columns}")

        for output_column in output_columns:
            sources: List[SourceTableAndColumn] | None = llm.get_column_lineage(output_column)
            if sources is None:
                continue

            validated_sources: List[SourceTableAndColumn] = []
            unvalidated_sources: List[SourceTableAndColumn] = sources or []
            incorrect_sources: List[SourceTableAndColumn] = []
            retry_limit = 3
            while retry_limit > 0:
                if retry_limit < 3:
                    print(f'try number: {3-retry_limit}')
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


