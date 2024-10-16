# llm-lineage

LLM Lineage is an LLM-based column lineage tool, built as part of the requirements for a final year project.

## Set Up
If you wish to explore LLM Lineage, you can do so by setting up a Docker instance on your personal computer. The steps to do so are documented below.

1. Clone the repository
2. Create a .env file and populate it with the variables specified in the .env.example file. A codebase you can use for testing is https://github.com/hearobe/analytics
3. Run `docker compose up`
    - Sometimes, the repo cloning step in the docker compose may throw an error. If this happens, you can clone the repository manually following the steps below:
      - Find the app container id by running `docker ps` in your terminal, and copy the id corresponding to the container called llm-lineage-app
      - Enter the container's shell by running `docker exec -it [container-id] sh`
      - Clone the repository by running `git clone [git repository URL] repo`. Please make sure the repository is in the repo directory.
      - Exit the container's shell and run `docker compose up` again
4. Test out the API at localhost:8000, or try the frontend site at localhost:3000 !
