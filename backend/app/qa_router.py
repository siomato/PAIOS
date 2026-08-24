from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.ai.ollama_provider import generate_qa_response


router = APIRouter(
    tags=["PAIOS Q&A"]
)


class QuestionRequest(BaseModel):
    question: str


@router.post("/ask")
def ask_question(request: QuestionRequest):

    question = (request.question or "").strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    print()
    print("========== PAIOS Q&A ==========")
    print(f"Question: {question}")
    print("===============================")

    try:

        answer = generate_qa_response(question)

        if answer is None:
            answer = ""

        answer = str(answer).strip()

        return {
            "status": "success",
            "answer": answer
        }

    except Exception as exc:

        print(f"PAIOS Q&A ERROR: {exc}")

        raise HTTPException(
            status_code=500,
            detail=f"PAIOS Q&A failed: {exc}"
        )