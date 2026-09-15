from typing_extensions import TypedDict

class State(TypedDict):
    message_history:str
    user_query:str

    message_id: str
    chat_jid: str
    sender_name:str
    sender: str
    sender_content: str
    timestamp: str
    is_from_me: bool
    past_conversation:list

    tool:bool
    tool_name:str
    tool_input:str
    tool_call_id:str
    availabe_tool:list

