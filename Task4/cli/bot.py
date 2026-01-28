from time import sleep
from dotenv import load_dotenv

load_dotenv()

from pipeline.rag import RAGEngine


rag = RAGEngine()


def handle_message(query: str):
    print("Thinking...")

    answer = rag.answer(query)

    print(answer)


def main():
    print("CLI RAG bot started")
    while True:
        query = input("Input query:")

        handle_message(query)

        sleep(1)


if __name__ == "__main__":
    main()
