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
    ingestor_thread = threading.Thread(target=start_ingestor, daemon=False)
    ingestor_thread.start()

if __name__ == "__main__":
    main()