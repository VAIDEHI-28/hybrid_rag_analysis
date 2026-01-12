from tools.tool_router import ToolRouter


def run_router_test():
    router = ToolRouter()

    questions = [
        "What is the total cost?",
        "Which vendor has the highest cost?",
        "Why is Hindalco Industries the top vendor?",
        "Explain the category Heavy Machinery",
    ]

    for q in questions:
        decision = router.route(q)
        print(f"\nQuestion: {q}")
        print(f"Decision: {decision}")


if __name__ == "__main__":
    run_router_test()
