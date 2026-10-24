import claude
import tools
global tokenCount
tokenCount = 0
def agent_loop(conversation):
    """Keep asking Claude, and running the tools it asks for, until it's done."""
    global tokenCount
    while True:
        if tokenCount > 100:
            print(f"The current token count is: {tokenCount}. Do you want to continue? [y/n]")
            user_input = input("")
            if user_input != "y":
                return False
            tokenCount = 0 

        message = claude.get_next_answer(conversation, tools.DEFINITIONS)

        tokenCount += message.usage.input_tokens + message.usage.output_tokens 
        # Every reply goes into the conversation, tool calls included: the API
        # matches each tool_result to a tool_use in the previous assistant message,
        # and wants the reply's thinking blocks sent back unchanged.
        # print(claude.get_token_estimate(message))
        conversation.append({"role": "assistant", "content": message.content})

        text = claude.text_of(message)
        if text:
            print("Nils :", text)

        if message.stop_reason != "tool_use":
            return False

        tool_calls = claude.tool_calls_of(message)
        results = tools.run(tool_calls)
        conversation.append({"role": "user", "content": results})


def main():
    conversation = []
    print("Nils 🪶 (Ctrl-D to quit)")
    try:
        while True:
            user_input = input("You: ")
            if not user_input.strip():
                continue

            conversation.append({"role": "user", "content": user_input})
            try:
                session = agent_loop(conversation)
                if not session:
                    return
                
            except claude.Unreachable as e:
                print(
                    f"Nils can't reach Claude right now: {e} Try again in a moment.")
    except (EOFError, KeyboardInterrupt):
        pass

if __name__ == "__main__":
    main()
