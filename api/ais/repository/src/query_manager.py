import json
import logging
import datetime
from datetime import datetime, timezone
import psycopg2
import psycopg2.extras
from psycopg2.extras import execute_values
import psycopg2.extensions
from psycopg2.extensions import connection
from typing import Callable
import threading

logger = logging.getLogger(__name__)

class QueryManager:
    '''
    Executes and manages client requests. If a client makes a database query,
    any outstanding queries by that client will be canceled in order to prevent spamming
    the database. Only the client's most recent request will be processed
    '''
    def __init__(self, pool):
        self.pool = pool
        self.client_to_query = {}  # client_id -> (conn, query_id)
        self.query_counter = 0
        self.lock = threading.Lock()

    def execute_query(self, query_func: Callable, client_id: str, *args, **kwargs):
        with self.lock:
            # Cancel old query if still running
            if client_id in self.client_to_query:
                old_conn, old_id = self.client_to_query[client_id]
                try:
                    logger.warning(f"Cancelling previous query ({old_id}) for client {client_id}")
                    old_conn.cancel()
                except Exception as e:
                    logger.warning(f"Failed to cancel query for {client_id}: {e}")
                finally:
                    self.pool.putconn(old_conn)
                    self.client_to_query.pop(client_id, None)

            # Start new query
            conn = self.pool.getconn()
            query_id = self.query_counter
            self.query_counter += 1
            self.client_to_query[client_id] = (conn, query_id)

        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            logger.info(f"Starting new query ({query_id}) for client {client_id}")
            results = query_func(cursor, *args, **kwargs)
            logger.info(f"Finished query ({query_id}) for client {client_id}")
            return results
        finally:
            cursor.close()
            with self.lock:
                # Only return to the pool if this is still the active query
                if client_id in self.client_to_query and self.client_to_query[client_id][1] == query_id:
                    self.pool.putconn(conn)
                    self.client_to_query.pop(client_id, None)

