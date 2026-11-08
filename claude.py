import anthropic

MODEL = "claude-haiku-5-5"

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment
Unreachable = anthropic.APIError

def get_next_answer(conversation, tools, model, systemPrompt=""):
    # """Send the whole conversation and the tools to Claude, and return its reply."""
    # return client.messages.create(
    #     model=model, max_tokens=20000, messages=conversation, tools=tools, system=systemPrompt
    # )
    """Send the whole conversation and tools to Claude."""
    with client.messages.stream(
        model=model,
        max_tokens=100000,
        messages=conversation,
        tools=tools,
        system=systemPrompt
    ) as stream:
        return stream.get_final_message()


def text_of(message):
    """The text of Claude's reply, without tool calls or thinking."""
    return "".join(block.text for block in message.content if block.type == "text")


def tool_calls_of(message):
    """The tools Claude asks us to run in this reply."""
    return [block for block in message.content if block.type == "tool_use"]

def get_token_estimate(message, model):
    # response = client.messages.count_tokens(message)
    response = client.messages.count_tokens(model=model, messages=[{"role": "user", "content": message.content}])
    return response.json()