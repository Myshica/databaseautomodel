# dbautomodel


Example:
```
import asyncio
from dbautomodel.module import DatabaseSqliteAPI


async def main():
    queries = [
        "CREATE TABLE users (user_id INTEGER PRIMARY KEY, name TEXT, email TEXT)",
        "CREATE TABLE messages (id INTEGER PRIMARY KEY, user_id INTEGER, message TEXT)"
    ]
    db = DatabaseSqliteAPI("./db.db", first_queries=queries)

    for user in await db.gets("users"):
        print(user.user_id)
        print(user.name)
        print(user.email)

    for message in await db.gets("messages"):
        print(message.id)
        print(message.user_id)
        print(message.message)


asyncio.run(main())
```

