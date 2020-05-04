import os

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
        self.credentials = {"user": "postgres", 
                            "password": "incredib!e", 
                            "database": "postgres", 
                            "host": "127.0.0.1"}
        bot.loop.create_task(self.init())

    async def init(self):
        self.pool = await asyncpg.create_pool(**self.credentials)
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