
import logging
logger = logging.getLogger(__name__)
import sys
from app import app

if __name__ == "__main__":
    import uvicorn
    # uvicorn.run(app, host="0.0.0.0", port=8000)
    uvicorn.run(app, host="0.0.0.0", port=3000, log_level="debug")
