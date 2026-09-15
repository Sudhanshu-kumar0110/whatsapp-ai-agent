from fastapi import FastAPI
from pydantic import BaseModel
from .agent_workflow import chat_ai
from client.rq_client import queue
import uvicorn

app = FastAPI()


class WhatsAppMessage(BaseModel):
    sender_name : str
    message_id: str
    chat_jid: str
    sender: str
    content: str
    timestamp: str
    is_from_me: bool


@app.post("/whatsapp/incoming")
async def whatsapp_message(message: WhatsAppMessage):

    # Ignore WhatsApp Status updates
    if message.chat_jid == "status@broadcast":
        print("⏭️ Ignoring WhatsApp status update")
        return {
            "success": True,
            "ignored": True
        }

    print("\n🔥 NEW WHATSAPP MESSAGE")
    print("Sender_name:",message.sender_name)
    print("Sender:", message.sender)
    print("Chat:", message.chat_jid)
    print("Message:", message.content)

    # Call your AI agent here
    user_message = f"""
        Sender Name: {message.sender_name}
        Sender: {message.sender}
        Chat: {message.chat_jid}

        Message:
        {message.content}
        """

    
    job = queue.enqueue(
        chat_ai,
        message.is_from_me,
        None,
        message.message_id,
        message.chat_jid,
        message.sender_name,
        message.sender,
        user_message,
        message.timestamp
    )

    return {
        "success": True,
        "job_id":job.id
    }

def main() :
    uvicorn.run("whatsapp_agent.agent_api:app", host="127.0.0.1", port=8000, reload=False)

main()