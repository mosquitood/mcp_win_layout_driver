import logging
import sys
from .driver import serve

def main() -> None:
    """MCP Window Layout Driver - Driver functionality for MCP"""
    import asyncio
    logging_level = logging.WARN
    logging.basicConfig(level=logging_level, stream=sys.stderr)
    asyncio.run(serve())

if __name__ == "__main__":
    main()