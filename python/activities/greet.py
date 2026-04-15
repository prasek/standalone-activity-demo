from dataclasses import dataclass

from temporalio import activity


@dataclass
class GreetingInput:
    greeting: str
    name: str


@activity.defn
def compose_greeting(input: GreetingInput) -> str:
    activity.logger.info(f"Running activity with input: {input}")
    return f"{input.greeting}, {input.name}!"
