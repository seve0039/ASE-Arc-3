import anthropic

MODEL = "claude-sonnet-5-5"

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment
Unreachable = anthropic.APIError

def get_next_answer(conversation, tools):
    """Send the whole conversation and the tools to Claude, and return its reply."""
    return client.messages.create(
        model=MODEL, max_tokens=1600, messages=conversation, tools=tools
    )


def text_of(message):
    """The text of Claude's reply, without tool calls or thinking."""
    return "".join(block.text for block in message.content if block.type == "text")


def tool_calls_of(message):
    """The tools Claude asks us to run in this reply."""
    return [block for block in message.content if block.type == "tool_use"]

def get_token_estimate(message):
    # response = client.messages.count_tokens(message)
    response = client.messages.count_tokens(model=MODEL, messages=[{"role": "user", "content": message.content}])
    return response.json()