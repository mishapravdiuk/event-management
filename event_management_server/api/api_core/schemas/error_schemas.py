from pydantic import BaseModel, Field


class ErrorModel(BaseModel):
    code: int = Field(default=400, description="http status code")
    title: str = Field(description="Error group")
    detail: str = Field(description="Details error")

    class Config:
        json_schema_extra = {
            "example": {
                "code": 400,
                "title": "IncorrectInputData",
                "detail": "Incorrect token",
            }
        }


class BadResponse(BaseModel):
    status: str = "error"
    data: ErrorModel
