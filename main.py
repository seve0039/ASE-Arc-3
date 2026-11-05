import claude
import tools
global costTotal
global permCost
costTotal = 0
permCost = 0
def agent_loop(conversation, userPrompt):
    """Keep asking Claude, and running the tools it asks for, until it's done."""
    global costTotal
    global permCost
    while True:
        if costTotal > 0.1:
            print(f"The current cost total is: {permCost}. Do you want to continue? [y/n]")
            user_input = input("")
            if user_input != "y":
                return False
            costTotal = 0 
            
        print(tools.MODEL)
        if tools.MODEL == "claude-haiku-5-5":
            evaluation_conversation = [
                {
                    "role": "user",
                    "content": (
                        f"Original user prompt:\n{userPrompt}\n\n"
                        "Evaluate whether Haiku's will be able to give a sufficient "
                        "and correct response for the original prompt. "
                        "Use the tool 'Escalate' if Haiku's response "
                        "wouln't be good enough. Otherwise, do nothing."
                    )
                }
            ]

            evaluation = claude.get_next_answer(
                evaluation_conversation,
                tools.DEFINITIONS,
                model="claude-sonnet-5-5",
                systemPrompt=(
                    "You are an evaluator. Assess the quality and "
                    "correctness of Haiku's response. Escalate if "
                    "necessary."
                )
            )
            costTotal += convertTokenPrice(evaluation.usage.input_tokens, evaluation.usage.output_tokens)

            evaluation_conversation.append({"role": "assistant", "content": evaluation.content})
            # print(evaluation.content)

            if len(claude.tool_calls_of(evaluation)) > 0: # if it wants to escalate
                text = claude.text_of(evaluation)
                if text:
                    print("Nils :", text)

                if evaluation.stop_reason != "tool_use":
                    return True

                tool_calls = claude.tool_calls_of(evaluation)
                results = tools.run(tool_calls)
                # evaluation_conversation.append({"role": "user", "content": results})
                

        message = claude.get_next_answer(conversation, tools.DEFINITIONS, model=tools.MODEL)
        costTotal += convertTokenPrice(evaluation.usage.input_tokens, evaluation.usage.output_tokens)
        permCost += costTotal
        print(f"The total cost is: ${permCost}")
         
        # Every reply goes into the conversation, tool calls included: the API
        # matches each tool_result to a tool_use in the previous assistant message,
        # and wants the reply's thinking blocks sent back unchanged.
        # print(claude.get_token_estimate(message))


        conversation.append({"role": "assistant", "content": message.content})

        text = claude.text_of(message)
        if text:
            print("Nils :", text)

        if message.stop_reason != "tool_use":
            return True

        tool_calls = claude.tool_calls_of(message)
        results = tools.run(tool_calls)
        conversation.append({"role": "user", "content": results})

def convertTokenPrice(input_token, output_token):
    if tools.MODEL == "claude-haiku-5-5":
        # From $0.10 / input MTok
        # From $0.50 / output MTok
        cost_input = (input_token / 1000000) * 0.1
        cost_output = (output_token / 1000000) * 0.5
        return cost_input + cost_output
    else: # sonnet 5.5 
        # $2 / input MTok
        # $10 / output MTok
        cost_input = (input_token / 1000000) * 2
        cost_output = (output_token / 1000000) * 10
        return cost_input + cost_output


def main():
    conversation = []
    print("Nils 🪶 (Ctrl-D to quit)")
    try:
        while True:
            user_input = input("You: ")
            if not user_input.strip():
                continue

            conversation.append({"role": "user", "content": user_input})
            # try:
            session = agent_loop(conversation, user_input)
            if not session:
                return
            
            # except claude.Unreachable as e:
            #     print(f"Nils can't reach Claude right now: {e} Try again in a moment.")
    except (EOFError, KeyboardInterrupt):
        pass

if __name__ == "__main__":
    main()
