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

class Database:
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.ready = False
        self.pool = None
        stream = os.popen('heroku config:get DATABASE_URL -a normobot')
        database_url = stream.read().strip()
        self.dsn = database_url
        bot.loop.create_task(self.init())

    async def init(self):        
        ssl_object = ssl.create_default_context()
        ssl_object.check_hostname = False
        ssl_object.verify_mode = ssl.CERT_NONE
#        self.pool = await asyncpg.create_pool(**self.credentials)
        self.pool = await asyncpg.create_pool(self.dsn, ssl=ssl_object)
        async with self.pool.acquire() as con:
            await con.execute(public)
            await con.execute(private)
            print("Ensured existence of task tables")
        self.ready = True

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