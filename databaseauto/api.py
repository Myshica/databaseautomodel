import os
import sqlite3
import aiosqlite


class DatabaseSqliteAPI:
    def __init__(self, path: str, first_query: str):
        self.path = path

        if not os.path.exists(self.path):
            self.create_tables(first_query)

    def create_tables(self, query: str):
        with sqlite3.connect(self.path) as db:
            db.execute(query)
            db.commit()

    def _query(self, query_str, args=None, fetch_all=None):
        with sqlite3.connect(self.path) as db:
            cursor = db.execute(query_str, args or ())
            db.commit()
            if fetch_all:
                return cursor.fetchall()
            else:
                return cursor.fetchone()

    async def query(self, query_str, args=None, fetch_all=None):
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

    def _schema(self, __d, __n) -> list:
        result = []
        for i in __d:
            if isinstance(i, tuple):
                r = {}
                for j in range(len(i)):
                    r[__n[j]] = i[j]
                result.append(type('model', (object,), r))
        return result

    async def gets(self, table: str) -> list:
        __n = await self.get_names_columns(table)
        __d = await self.query(f"SELECT * FROM {table}", (), True)
        return self._schema(__d, __n)

    async def get(self, id: str, table: str, find_all=False) -> list:
        query = f"SELECT * FROM {table} WHERE {id}"
        __n = await self.get_names_columns(table)
        __d = await self.query(query, (), find_all)
        return self._schema(__d, __n)

    async def add(self, table: str, **kwargs) -> list:
        columns = ', '.join(kwargs.keys())
        placeholders = ', '.join('?' for _ in kwargs)
        values = tuple(kwargs.values())
        query_str = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        __n = await self.get_names_columns(table)
        __d = await self.query(query_str, args=values)
        return self._schema(__d, __n)

    async def set(self, condition: str, table: str, **kwargs) -> list:
        cols = ', '.join([f"{key} = '{value}'" for key, value in kwargs.items()])
        __n = await self.get_names_columns(table)
        __d = await self.query(f"UPDATE {table} SET {cols} WHERE {condition}", ())
        return self._schema(__d, __n)

    async def dels(self, table: str) -> bool:
        await self.query(f"DELETE FROM {table}", ())
        return True

    async def del_(self, id: str, table: str) -> bool:
        await self.query(f"DELETE FROM {table} WHERE {id}", ())
        return True
