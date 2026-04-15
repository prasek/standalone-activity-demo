import asyncio
from datetime import timedelta

from temporalio.client import Client
from temporalio.envconfig import ClientConfig

from activities.greet import GreetingInput, compose_greeting

TASK_QUEUE = "saa-demo"


async def main():
    # Loads connection config from environment variables (TEMPORAL_ADDRESS, etc.)
    # Falls back to localhost:7233 for local dev server
    connect_config = ClientConfig.load_client_connect_config()
    connect_config.setdefault("target_host", "localhost:7233")
    client = await Client.connect(**connect_config)

    # Execute a standalone activity (start + wait for result)
    print("Executing standalone activity...")
    result = await client.execute_activity(
        compose_greeting,
        args=[GreetingInput("Hello", "World")],
        id="greeting-1",
        task_queue=TASK_QUEUE,
        start_to_close_timeout=timedelta(seconds=10),
    )
    print(f"Result: {result}")

    # Start a standalone activity (non-blocking) and get result later
    print("\nStarting standalone activity (non-blocking)...")
    handle = await client.start_activity(
        compose_greeting,
        args=[GreetingInput("Hi", "Temporal")],
        id="greeting-2",
        task_queue=TASK_QUEUE,
        start_to_close_timeout=timedelta(seconds=10),
    )
    print(f"Activity started with ID: {handle.id}")
    result = await handle.result()
    print(f"Result: {result}")


if __name__ == "__main__":
    asyncio.run(main())
