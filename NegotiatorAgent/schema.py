from pydantic import BaseModel, Field
from typing import Optional

class Greet_Intro_Response(BaseModel):
    greet_intro: str = Field(description="Greet the user and share the short brand intro and campaign details")

class CheckBudgetInterest(BaseModel):
    interest_response: bool = Field(description="If the user said yes or gave positive signs to know the budget or said okay or ok then strictly assign boolean interest_response True or else False")
    other_query: bool = Field(description="If user asked some query which is not positive or negative then assign boolean other_query True if else False as default")

class Deal(BaseModel):
    isDeal: bool = Field(..., description="Set to True if the user agrees to the deal or gives a positive response; otherwise, False, if the input is invalid then assign False as default")
    user_price: int = Field(
        description="Final price the user is comfortable with. Must be extracted from the user's response, even if they agree directly. Assign -1 if the input is invalid"
    )
    message: str = Field(description="End message by LLM")