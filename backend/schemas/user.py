from pydantic import BaseModel, ConfigDict, Field, field_validator

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    admin: bool
    #chat_id: str | None = None

"""class ChatIdUpdate(BaseModel):
    chat_id: str = Field(min_length=1, max_length=50)

class ChatIdResponse(BaseModel):
    chat_id: str"""