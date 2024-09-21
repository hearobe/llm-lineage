from typing import Union

from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel

from api_methods import initiate_lineage_trace

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/lineage")
def get_lineage(column_name: str, table_name: str):
    return {"column_name": column_name, "table_name": table_name}

@app.post("/request-lineage-trace")
def request_lineage_trace(background_tasks: BackgroundTasks):
    background_tasks.add_task(initiate_lineage_trace)
    return {"message": "Lineage trace started"}

class LineageTraceStatus(BaseModel):
    succeeded: bool
    error_message: Union[str, None]

@app.webhooks.post("lineage-trace-status")
def lineage_trace_status(body: LineageTraceStatus):
    """
    When the frontend requests a lineage trace, they should subscribe to this service.
    A POST request will be sent when the trace has completed or has terminated early due to an error.
    """
