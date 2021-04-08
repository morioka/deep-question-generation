from pydantic import BaseModel, Field
from typing import List

# request
class AnswerContext(BaseModel):
    answer: str = Field(description="解答", example="富士山")
    context: str = Field(description="文脈", example="日本で一番高い山は富士山です。")

class AnswerContextList(BaseModel):
    answer_context: List[AnswerContext]

# response
class GeneratedQuestion(BaseModel):
    question: str = Field(description="生成された疑問文", example="日本で一番高い山は何ですか")

class GeneratedQuestionList(BaseModel):
    questions: List[GeneratedQuestion]
