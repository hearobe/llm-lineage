from pathlib import Path
from typing import List
import yaml

class FileService:
    def __init__(self):
        print("Initializing FileService")

        # find root of repo
        repo_paths: List[Path] = []
        for path in Path().rglob("repo/"):
            repo_paths.append(path)
        if len(repo_paths) != 1:
            raise Exception(f"{len(repo_paths)} paths found for repo. Only 1 should be present")
        
        self.repo_root = repo_paths[0]

        # find root of dbt project within repo
        dbt_project_file_paths: List[Path] = []
        for path in Path(self.repo_root).rglob("dbt_project.y*ml"):
            dbt_project_file_paths.append(path)
        if len(dbt_project_file_paths) != 1:
            raise Exception(f"{len(dbt_project_file_paths)} dbt project files found for repo. Only 1 should be present")
        
        self.dbt_project_file_path = dbt_project_file_paths[0]
        self.dbt_project_dir_path = self.dbt_project_file_path.parent

        # TESTING
        print("FileService initialized")
        print(self.repo_root)
        print(self.dbt_project_file_path)
        print(self.dbt_project_dir_path)
    
    def get_schema_and_model_files(self):
        print("in get_schema_and_model_files")

        # find directories where models are stored (specified in dbt_project.yml)
        dbt_project_file = yaml.safe_load(open(self.dbt_project_file_path))
        model_paths = [self.dbt_project_dir_path.joinpath(x) for x in dbt_project_file["model-paths"]]

        print(dbt_project_file)
        print(dbt_project_file["model-paths"])
        print(model_paths)

        # push yml and sql files in model paths into schema and model file arrays
        schema_files: List[Path] = []
        model_files: List[Path] = []
        for root in model_paths:
            for file in Path(root).rglob("*.y*ml"):
                schema_files.append(file)
            for file in Path(root).rglob("*.sql"):
                model_files.append(file)

        return schema_files, model_files
