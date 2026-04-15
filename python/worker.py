import asyncio
from concurrent.futures import ThreadPoolExecutor

from temporalio.client import Client
from temporalio.envconfig import ClientConfig
from temporalio.worker import Worker

from activities.greet import compose_greeting

TASK_QUEUE = "saa-demo"


async def main():
    # Loads connection config from environment variables (TEMPORAL_ADDRESS, etc.)
    # Falls back to localhost:7233 for local dev server
    connect_config = ClientConfig.load_client_connect_config()
    connect_config.setdefault("target_host", "localhost:7233")
    client = await Client.connect(**connect_config)

    with ThreadPoolExecutor(max_workers=5) as executor:
        worker = Worker(
            client,
            task_queue=TASK_QUEUE,
            activities=[compose_greeting],
            activity_executor=executor,
        )
        print(f"Worker listening on task queue: {TASK_QUEUE}")
        await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
