import os
import ssl

import asyncpg
from discord.ext import commands

public = """CREATE TABLE IF NOT EXISTS public_tasks (
                       id SERIAL,
                       author BIGINT, 
                       description VARCHAR (255) NOT NULL
            )"""

private = """CREATE TABLE IF NOT EXISTS private_tasks (
                       id SERIAL,
                       author BIGINT, 
                       description VARCHAR (255) NOT NULL
            )"""

contributors = """CREATE TABLE IF NOT EXISTS contributors (
                       author BIGINT UNIQUE
            )"""

class Database:
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.ready = False
        self.pool = None
        database_url = os.environ['DATABASE_URL']
        self.dsn = database_url
        bot.loop.create_task(self.init())

    async def init(self):        
        self.pool = await asyncpg.create_pool(self.dsn)
        async with self.pool.acquire() as con:
            await con.execute(public)
            await con.execute(private)
            print("Ensured existence of task tables")
        self.ready = True

    async def enter_contributor(self, author_id):
        sql = "INSERT INTO contributors(author) VALUES($1);"
        async with self.pool.acquire() as con:
            await self.pool.execute(sql, author_id)

    async def get_contributor(self, author_id):
        sql = "SELECT * FROM contributors WHERE author = $1;"
        async with self.pool.acquire() as con:
            row = await con.fetchrow(sql, author_id)
        return row

    async def enter_public_task(self, author_id, description):
        sql = "INSERT INTO public_tasks(author, description) VALUES($1, $2);"
        async with self.pool.acquire() as con:
            await self.pool.execute(sql, author_id, description)

    async def query_public_tasks(self, identity):
        sql = "SELECT * FROM public_tasks WHERE id = $1;"
        async with self.pool.acquire() as con:
            row = await con.fetchrow(sql, identity)
        return row

    async def delete_public_task(self, identity):
        sql = "DELETE FROM public_tasks WHERE id = $1 RETURNING *;"
        async with self.pool.acquire() as con:
            deleted_row = await con.fetchrow(sql, identity)         
        return deleted_row

    async def get_public_tasks(self):
        sql = "SELECT * FROM public_tasks;"
        async with self.pool.acquire() as con:
            tasks = await con.fetch(sql)
        return tasks

    async def get_public_task_amount(self):
        table = await self.get_public_tasks()
        return len(table)

    async def drop_tasks(self):
        sql = "DROP TABLE private_tasks, public_tasks;"
        async with self.pool.acquire() as con:
            await con.execute(sql)
            await con.execute(public)
            await con.execute(private)