import logging
from mcp.server.stdio import stdio_server
from mcp.server import Server
from mcp.types import (
    TextContent,
    Tool,
)
from enum import Enum
from pydantic import BaseModel

class GetProcessList(BaseModel):
    pass

class GetProcessByname(BaseModel):
    name: str

class GetProcessStatus(BaseModel):
    name: str

class StartProcess(BaseModel):
    name: str

class StopProcess(BaseModel):
    name: str

class SetProcessName(BaseModel):
    name: str
    new_name: str


class DriverTools(str, Enum):
    GET_PROCESS_LIST = "get_process_list"
    GET_PROCESS_BY_NAME = "get_process_by_name"
    GET_PROCESS_STATUS = "get_process_status"
    STOP_PROCESS = "stop_process"
    START_PROCESS = "start_process"
    SET_PROCESS_NAME = "set_process_name"


def get_process_list() -> list:
    """Get a list of all processes running on the system."""
    return [
        {
            "name": "Process 1",
            "status": "Running",
            "pid": 12345
        },
        {
            "name": "Process 2",
            "status": "Stopped",
            "pid": 12346
        },
        {
            "name": "Process 3",
            "status": "Running",
            "pid": 12347
        },
        {
            "name": "Process 4",
            "status": "Pending",
            "pid": 12348
        }
    ]

def get_process_by_name(name: str) -> dict:
    """Get a process by name.

    Args:
        name: The name of the process
    """
    return next((process for process in get_process_list() if process["name"] == name), None)

async def get_process_status(name: str) -> str:
    """Get the status of a process.

    Args:
        name: The name of the process
    """
    processes = get_process_list()
    for process in processes:
        if process["name"] == name:
            return process["status"]
    return "Process not found"

async def start_process(name: str) -> str:
    """Start a process.

    Args:
        name: The name of the process
    """
    return "Process started"

async def stop_process(name: str) -> str:
    """Stop a process.

    Args:
        name: The name of the process
    """
    return "Process stopped"

async def set_process_name(name: str, new_name: str) -> str:
    """Set the name of a process.

    Args:
        name: The name of the process
        new_name: The new name of the process
    """
    return "Process name set"


async def serve() -> None:
    logger = logging.getLogger(__name__)
    server = Server("driver")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name=DriverTools.GET_PROCESS_LIST,
                description="Get a list of all processes running on the system",
                inputSchema=GetProcessList.schema(),

            ),
            Tool(
                name=DriverTools.GET_PROCESS_BY_NAME,
                description="Get a process by name",
                inputSchema=GetProcessByname.schema(),
            ),
            Tool(
                name=DriverTools.GET_PROCESS_STATUS,
                description="Get the status of a process",
                inputSchema=GetProcessStatus.schema(),
            ),
            Tool(
                name=DriverTools.START_PROCESS,
                description="Start a process",
                inputSchema=StartProcess.schema(),
            ),
            Tool(
                name=DriverTools.STOP_PROCESS,
                description="Stop a process",
                inputSchema=StopProcess.schema(),
            ),
            Tool(
                name=DriverTools.SET_PROCESS_NAME,
                description="Set the name of a process",
                inputSchema=SetProcessName.schema(),
            ),
            Tool(
                name=DriverTools.GET_PROCESS_STATUS,
                description="Get the status of a process",
                inputSchema=GetProcessStatus.schema(),
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        if name == DriverTools.GET_PROCESS_LIST:
            result = get_process_list()
            return [TextContent(text=result)]
        elif name == DriverTools.GET_PROCESS_BY_NAME:
            result = get_process_by_name(arguments["name"])
            return [TextContent(text=result)]
        elif name == DriverTools.GET_PROCESS_STATUS:
            result = get_process_status(arguments["name"])
            return [TextContent(text=result)]
        elif name == DriverTools.START_PROCESS:
            result = start_process(arguments["name"])
            return [TextContent(text=result)]
        elif name == DriverTools.STOP_PROCESS:
            result = stop_process(arguments["name"])
            return [TextContent(text=result)]
        elif name == DriverTools.SET_PROCESS_NAME:
            result = set_process_name(arguments["name"], arguments["new_name"])
            return [TextContent(text=result)]   
        else:
            raise ValueError(f"Unknown tool: {name}")

    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options, raise_exceptions=True)