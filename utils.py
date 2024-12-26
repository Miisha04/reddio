import json
import logging
from typing import Optional
import aiofiles

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def read_json(path: str, encoding: Optional[str] = None) -> list | dict:
    try:
        #logger.info(f"Opening file: {path}")
        async with aiofiles.open(path, mode='r', encoding=encoding) as file:
            content = await file.read()
            #logger.info("File successfully read")
            return json.loads(content)
    except Exception as e:
        logger.error(f"Unexpected error while reading file: {e}", exc_info=True)
        raise
