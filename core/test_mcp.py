import asyncio
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER = str(Path(__file__).parent / "mcp_server.py")


async def main():
    params = StdioServerParameters(command=sys.executable, args=[SERVER])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print("Tools:", [t.name for t in tools.tools])

            result = await session.call_tool("timetable", {"class_name": "5", "day": "Monday"})
            print(result.content[0].text)

            result = await session.call_tool("policy_search", {"question": "Is there a school bus?"})
            print(result.content[0].text[:200])


asyncio.run(main())