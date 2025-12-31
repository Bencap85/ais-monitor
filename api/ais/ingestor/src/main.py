import asyncio
import json
from datetime import datetime, timezone
import time
import random
import os
import threading
import logging
from ingestor import AisIngestor
from settings import Settings
from server import create_app


logger = logging.getLogger(__name__)
settings = Settings()

logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )

def start_ingestor():
    ingestor = AisIngestor()
    ingestor.run()

def main():
    ingestor = AisIngestor()
    app = create_app()
    app.producer = ingestor

    ingestor_thread = threading.Thread(target=ingestor.run, daemon=False)
    ingestor_thread.start()

    app.run(host='0.0.0.0', port=8081)

if __name__ == "__main__":
    main()