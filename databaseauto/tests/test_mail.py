import asyncio

from database_auto_model.api import DatabaseSqliteAPI


async def main():
    get_users = await DatabaseSqliteAPI("./db.db", first_query="SELECT * FROM users").gets()
    print(get_users)
    for user in get_users:
        print(user)


asyncio.run(main())