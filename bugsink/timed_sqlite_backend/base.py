import time
from contextlib import contextmanager

from django.db.backends.sqlite3.base import (
    DatabaseWrapper as UnpatchedDatabaseWrapper, SQLiteCursorWrapper as UnpatchedSQLiteCursorWrapper,
)


@contextmanager
def limit_runtime(conn, seconds):
    start = time.time()

    def check_time():
        if time.time() > start + seconds:
            return 1

    # Set the progress handler to check the time; 10_000 is the number of SQLite VM instructions between invocations;
    # Simon Willison's experiments in Datasette suggest to use 1_000 here; but I don't care about precision so much
    # (it's just a final backstop) and I want to avoid the calls-into-Python (expensive!) as much as possible so I pick
    # a higher value.
    conn.set_progress_handler(check_time, 10_000)
    yield

    conn.set_progress_handler(None, 0)


class PrintOnClose(object):
    def __init__(self, conn):
        self.conn = conn

    def __getattr__(self, item):
        return getattr(self.conn, item)

    def close(self):
        print("Connection closed", id(self.conn))
        self.conn.close()


class DatabaseWrapper(UnpatchedDatabaseWrapper):

    # def get_new_connection(self, conn_params):
    #     result = super().get_new_connection(conn_params)
    #     import threading
    #     print("Connection created", conn_params["database"], id(result), threading.current_thread().name)
    #     return PrintOnClose(result)

    def create_cursor(self, name=None):
        return self.connection.cursor(factory=SQLiteCursorWrapper)


class SQLiteCursorWrapper(UnpatchedSQLiteCursorWrapper):

    def execute(self, query, params=None):
        with limit_runtime(self.connection, 5.0):
            return super().execute(query, params)

    def executemany(self, query, param_list):
        with limit_runtime(self.connection, 5.0):
            return super().executemany(query, param_list)
