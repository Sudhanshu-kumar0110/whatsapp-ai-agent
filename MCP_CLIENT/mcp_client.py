
import sys
from pathlib import Path
from langchain_mcp_adapters.client import MultiServerMCPClient
from whatsapp_agent.state import State

server_dir = (
    Path(__file__).resolve().parent.parent
    / "whatsapp-mcp"
    / "whatsapp-mcp-server"
)

client = MultiServerMCPClient({
    "whatsapp": {
        "transport": "stdio",
        "command": sys.executable,
        "args": [
            "main.py"
        ],
        "cwd": str(server_dir),
    }
})

fetch_tool = None
tool_map = None
async def get_tool():
    global fetch_tool
    global tool_map

    if fetch_tool is not None :
        return fetch_tool,tool_map
    
    fetch_tool = await client.get_tools()
    tool_map = {
        tool.name: tool 
        for tool in fetch_tool
    }
    return fetch_tool,tool_map

async def call_tool(state:State) :
    await get_tool()
    tool = tool_map.get(state["tool_name"])
    if tool is None :

        return {
            "error":f"Tool '{state['tool_name']}' not found"
        }
    else :

        try :

            result = await tool.ainvoke(state["tool_input"])
            return result
        except Exception as e :
            return {
                "error":str(e)
            }