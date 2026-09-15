from fastapi import APIRouter
from app.ai.manager import ask_ai
router=APIRouter()
@router.post('/chat')
def chat(message:dict):
    text=str(message.get('message','') or '').strip()
    if not text:return {'reply':'','status':'empty_input'}
    result=ask_ai(text)
    return {'reply':result,'status':'success'}
