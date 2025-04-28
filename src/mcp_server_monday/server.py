import asyncio
import importlib.metadata
import logging

import mcp.server.stdio
import mcp.server.websocket
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from monday import MondayClient

from mcp_server_monday.constants import MONDAY_API_KEY
from mcp_server_monday.tools import (
    register_tools,
)

# 日志既写入文件也输出到控制台，级别为DEBUG
log_formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s')
logger = logging.getLogger("mcp-server-monday-qi")
logger.setLevel(logging.DEBUG)

# 文件日志
file_handler = logging.FileHandler('logs/server.log', encoding='utf-8')
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.DEBUG)
logger.addHandler(file_handler)

# 控制台日志
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
console_handler.setLevel(logging.DEBUG)
logger.addHandler(console_handler)


monday_client = None
server = Server("monday")


async def main():
    logger.info("Starting Monday.com MCP server")
    global monday_client
    try:
        monday_client = MondayClient(MONDAY_API_KEY)
        logger.info("Step 2: MondayClient initialized")
    except Exception as e:
        logger.error(f"Failed to initialize MondayClient: {e}", exc_info=True)
        raise
    register_tools(server, monday_client)
    logger.info("Step 3: Tools registered")
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        logger.info("Step 4: Entered stdio server context")
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="monday",
                server_version=importlib.metadata.version("mcp-server-monday-qi"),
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
