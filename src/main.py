from typing import Union

from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from api_methods import get_lineage_of_column, initiate_lineage_trace, validate_lineage_trace
from test import manual_testing

origins = [
    "http://localhost",
    "http://localhost:3000",
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/lineage")
def get_lineage(column_name: str, table_name: str, downstream_only: bool = False, upstream_only: bool = False):
    return get_lineage_of_column(column_name, table_name, downstream_only, upstream_only)

@app.post("/request-lineage-trace")
def request_lineage_trace(background_tasks: BackgroundTasks):
    validate_lineage_trace()
    background_tasks.add_task(initiate_lineage_trace)
    return {"message": "Lineage trace started"}

@app.post("/test")
def test():
    manual_testing()
    return {"message": "initiated test"}

class LineageTraceStatus(BaseModel):
    succeeded: bool
    error_message: Union[str, None]

@app.webhooks.post("lineage-trace-status")
def lineage_trace_status(body: LineageTraceStatus):
    """
    When the frontend requests a lineage trace, they should subscribe to this service.
    A POST request will be sent when the trace has completed or has terminated early due to an error.
    """
