from nova.brain import NovaBrain


def main():
    print("Nova v0.1 — The Spark")
    print("Type 'quit' to exit.\n")

    nova = NovaBrain()
    conversation_history = []

    try:
        while True:
            user_input = input("You: ").strip()

            if user_input.lower() in ("quit", "exit"):
                print("Nova: Goodbye!")
                break

            if not user_input:
                continue

            reply = nova.think(user_input, conversation_history)

            conversation_history.append({"role": "user", "content": user_input})
            conversation_history.append({"role": "assistant", "content": reply})

            print(f"Nova: {reply}\n")
    finally:
        nova.close()


if __name__ == "__main__":
    main()
