import os
import sqlite3
import aiosqlite


class DatabaseSqliteAPI:
    def __init__(self, path: str, first_queries: list[str]):
        '''
        path: PATH to db,
        first_queries: FIRST queries to create tables

        :param path:
        :param first_queries:
        '''

        self.path = path

        if not os.path.exists(self.path):
            self.create_tables(first_queries)

    def create_tables(self, first_queries: list[str]):
        with sqlite3.connect(self.path) as db:
            for query in first_queries:
                db.execute(query)
            db.commit()

    def _query(self, query_str: str, args: tuple = None, fetch_all: bool = None):
        with sqlite3.connect(self.path) as db:
            cursor = db.execute(query_str, args or ())
            db.commit()
            if fetch_all:
                return cursor.fetchall()
            else:
                return cursor.fetchone()

    async def query(self, query_str: str, args: tuple = None, fetch_all: bool = None):
        async with aiosqlite.connect(self.path) as db:
            cursor = await db.execute(query_str, args or ())
            await db.commit()
            if fetch_all:
                return await cursor.fetchall()
            else:
                return await cursor.fetchone()

    async def get_names_columns(self, table: str):
        __d = await self.query(f"PRAGMA table_info({table})", fetch_all=True)
        return [i[1] for i in __d]

    def _schema(self, __d: list[tuple], __n: list, _table: str) -> list:
        result = []
        for i in __d:
            if isinstance(i, tuple):
                r = {}
                for j in range(len(i)):
                    r[__n[j]] = i[j]
                result.append(type(f'{_table}_model', (object,), r))
        return result

    async def gets(self, table: str) -> list:
        __n = await self.get_names_columns(table)
        __d = await self.query(f"SELECT * FROM {table}", (), True)
        return self._schema(__d, __n, table)

    async def get(self, id: str, table: str, find_all=False) -> list:
        query = f"SELECT * FROM {table} WHERE {id}"
        __n = await self.get_names_columns(table)
        __d = await self.query(query, (), find_all)
        return self._schema(__d, __n, table)

    async def add(self, table: str, **kwargs) -> bool:
        columns = ', '.join(kwargs.keys())
        placeholders = ', '.join('?' for _ in kwargs)
        values = tuple(kwargs.values())
        query_str = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        __n = await self.get_names_columns(table)
        __d = await self.query(query_str, args=values)
        return True

    async def set(self, condition: str, table: str, **kwargs) -> bool:
        cols = ', '.join([f"{key} = '{value}'" for key, value in kwargs.items()])
        __n = await self.get_names_columns(table)
        __d = await self.query(f"UPDATE {table} SET {cols} WHERE {condition}", ())
        return True

    async def dels(self, table: str) -> bool:
        await self.query(f"DELETE FROM {table}", ())
        return True

    async def del_(self, id: str, table: str) -> bool:
        await self.query(f"DELETE FROM {table} WHERE {id}", ())
        return True
