from pydantic import BaseModel, ConfigDict

class TelegramAccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    username: str
    chat_id: int

class TelegramAccountConnection(BaseModel):
    connection_link: str
    connection_code: str

class TelegramAccountListResponse(BaseModel):
    items: list[TelegramAccountResponse]
    page: int
    total: int
    pages: int
