from pydantic import BaseModel

class IngestRequest(BaseModel):
    folder: str = "./input"

class AskRequest(BaseModel):
    query: str

class AskResponse(BaseModel):
    answer: str
