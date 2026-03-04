import sys
sys.dont_write_bytecode = True

import asyncio
import os
from dotenv import load_dotenv
from bot.client import MiBotClient
from bot.instance import client
from cache.redis_manager import connect_redis
from database.mongo import connect_db, close_mongo

from utils.cogs_functions import clear_console, pre_loading
load_dotenv()
token = os.getenv("DISCORD_BOT_TOKEN")

# Discord Bot Client
async def start_client():
    await client.start(token)

# Service Initalizations
# Service file MUST HAVE a startService() function
async def start_services():
    for service in os.listdir('./runtime'):
        if service.endswith('.py'):
            service_module = f'runtime.{service[:-3]}'
            module = __import__(service_module, fromlist=['startService'])
            start_service = getattr(module, 'startService', None)
            if start_service:
                print(f'Started service: {service_module}')
                asyncio.create_task(start_service())
            else:
                print(f'Cannot start function due to missing start function in {service_module}')

async def start_db():
    asyncio.create_task(connect_db())

async def stop_db():
    asyncio.create_task(close_mongo())

async def start_redis(client : MiBotClient):
    asyncio.create_task(connect_redis(client))

# Main Function
async def system():
    await asyncio.gather(
        start_client(),
        start_services(),
        start_db(),
        start_redis(client)
    )

async def shutdown_bot():
    await client.close()

if __name__ == "__main__":
    try:
        clear_console()
        pre_loading()
        asyncio.run(system())
    except KeyboardInterrupt:
        # print("Shutting down services...")
        # asyncio.run(stop_db()) # To fix
        asyncio.run(shutdown_bot())