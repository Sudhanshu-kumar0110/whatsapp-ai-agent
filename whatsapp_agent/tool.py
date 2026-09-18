from .state import State
from MCP_CLIENT.mcp_client import get_tool ,call_tool
import json
from .prompt import SYSTEM_PROMPT
from openai import OpenAI
import os 
from dotenv import load_dotenv


load_dotenv()


async def reterive_conversation(state:State):

    fetch_tool,tool_map = await get_tool()
    state["availabe_tool"] = openai_tool_formate(fetch_tool)
    tool = tool_map["list_messages"]
    result = await tool.ainvoke(
        {
            'chat_jid':state.get("chat_jid"),
            'include_context':False,
            'limit':50
        }
    )

    messages = []

    for item in reversed(result):
        msg = json.loads(item["text"])

        sender = "Me" if msg["is_from_me"] else msg["chat_name"]
        content = msg["content"]

        messages.append(f"{sender}: {content}")

    state["past_conversation"] = messages

    return state

def message_history(state:State):
    state["message_history"] = [{"role":"system","content":SYSTEM_PROMPT(state)},
                       {"role":"user","content":state.get('sender_content')}]
    
    return state

def openai_tool_formate(tools):

    openai_tool = []

    for tool in tools:

        openai_tool.append({
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description or "",
                "parameters": tool.args_schema
            }
        })

    return openai_tool

async def whatsapp_agent(state:State):

    client = OpenAI(
        api_key=os.getenv("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1"
    )

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=state.get("message_history"),
        tools=state.get("availabe_tool"),
        tool_choice={"type": "function", "function": {"name": "send_message"}}
    )

    message = response.choices[0].message

    state["tool"] = False
    state["tool_name"] = None 
    state["tool_input"] = None

    if message.tool_calls :

        tool_call = message.tool_calls[0]

        state["tool"] = True
        state["tool_name"] = tool_call.function.name
        state["tool_input"] = json.loads(tool_call.function.arguments)
        state["tool_call_id"] = tool_call.id

        state["message_history"].append({
            "role":"assistant",
            "content":None,
            "tool_calls":[
                {
                    "id":state["tool_call_id"],
                    "type":"function",
                    "function":{
                        "name":state["tool_name"],
                        "arguments":json.dumps(state["tool_input"])
                    }
                }
            ]
        })

        return state 
    content = message.content

    state["message_history"].append({
        "role":"assistant",
        "content":content
    })

    return state 


async def evalaute_response(state:State):

    print("========== TOOL EXECUTION ==========")
    print("TOOL:", state.get("tool"))
    print("TOOL NAME:", state.get("tool_name"))
    print("TOOL INPUT:", state.get("tool_input"))
    print("TOOL CALL ID:", repr(state.get("tool_call_id")))
    print("====================================")

    if state["tool"] :

        if not state["tool_call_id"]:
            raise ValueError(
                f"tool_call_id is missing! State = {state}"
            )
        if str(state["tool_name"]) != "send_message" :
            state["message_history"].append({
                                "role": "tool",
                                "tool_call_id": state["tool_call_id"],
                                "content": "You don't have access to use this tool"
                            })

            state["tool"] = False
            return "whatsapp_agent"

        tool_response = await call_tool(state)

        print("tool response:",tool_response)

        response = json.loads(tool_response[0]['text'])

        if response["success"] == True :
            return "endnode"
        else :
            tool_response = tool_response[0]['text']
        
        state["message_history"].append({
                    "role": "tool",
                    "tool_call_id": state["tool_call_id"],
                    "content": tool_response
                })

        state["tool"] = False 

        return "whatsapp_agent"

    return "endnode"

def endnode(state:State):
    return state
