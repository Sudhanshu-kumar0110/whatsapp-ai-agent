from langgraph.graph import StateGraph,START,END
from langgraph.checkpoint.mongodb import MongoDBSaver
from .tool import *

DB_URL = "mongodb://admin:admin@localhost:27017"

graph_builder = StateGraph(State)

graph_builder.add_node("reterive_conversation",reterive_conversation)
graph_builder.add_node("message_history",message_history)
graph_builder.add_node("whatsapp_agent",whatsapp_agent)
graph_builder.add_node("evalaute_response",evalaute_response)
graph_builder.add_node("endnode",endnode)

graph_builder.add_edge(START,"reterive_conversation")
graph_builder.add_edge("reterive_conversation","message_history")
graph_builder.add_edge("message_history","whatsapp_agent")
graph_builder.add_conditional_edges("whatsapp_agent",evalaute_response)

graph_builder.add_edge("endnode",END)

def compile_graph_with_checkpoint(checkpointer):
    return graph_builder.compile(checkpointer=checkpointer)

async def chat_ai(
        is_from_me:bool,
        user_query:str = None,
        message_id:str = None,
        chat_jid:str = None ,
        sender_name:str = None,
        sender:str = None,
        sender_content:str = None,
        timestamp:str = None,        
):

    config = {
        "configurable":{
            "thread_id":f"{chat_jid}"
        }
    }

    state = State({
        "user_query": user_query,
        "llm_output": [],
        "message_id":message_id,
        "chat_jid":chat_jid,
        "sender_name":sender_name,
        "sender":sender,
        "sender_content":sender_content,
        "timestamp":timestamp,
        "is_from_me":is_from_me,
        })
    
    with MongoDBSaver.from_conn_string(DB_URL) as checkpointer:
        graph = compile_graph_with_checkpoint(checkpointer)
        result = await graph.ainvoke(state, config=config)
    
    # return result["llm_output"] 