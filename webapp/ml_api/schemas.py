from pydantic import BaseModel, Field
from typing import List

# request
class AnswerContext(BaseModel):
    answer: str = Field(description="正解", example="富士山")
    context: str = Field(description="文脈", example="日本で一番高い山は富士山です。")

class AnswerContextList(BaseModel):
    answer_context: List[AnswerContext]

class Text(BaseModel):
    text: str

class Data(BaseModel):
    data: List[Text]

# response
class Output(Text):
    sentiment: str

class Pred(BaseModel):
    prediction: List[Output]

class GeneratedQuestion(BaseModel):
    question: str = Field(description="生成されたクイズ文", example="日本で一番高い山は何ですか")

class GeneratedQuestionList(BaseModel):
    questions: List[GeneratedQuestion]
#    questions: List[str]
