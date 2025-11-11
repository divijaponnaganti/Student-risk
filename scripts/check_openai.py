import os
import sys

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

try:
    from langchain_openai import ChatOpenAI
except Exception as e:
    print("OPENAI IMPORT ERROR:", type(e).__name__, str(e))
    sys.exit(1)

def main():
    key = os.getenv("OPENAI_API_KEY")
    print("Key present:", bool(key))
    if not key:
        print("CONNECTED:", False)
        return

    try:
        print("Creating client...")
        llm = ChatOpenAI(api_key=key, model="gpt-3.5-turbo")
        print("Client created:", llm is not None)
    except Exception as e:
        print("OpenAI client error:", type(e).__name__, str(e)[:500])
        print("CONNECTED:", False)
        return

    try:
        print("Invoking test message...")
        resp = llm.invoke("Hello")
        ok = bool(resp and getattr(resp, "content", None))
        print("OpenAI call succeeded:", ok)
        print("CONNECTED:", ok)
    except Exception as e:
        print("OpenAI call error:", type(e).__name__, str(e)[:500])
        print("CONNECTED:", False)

if __name__ == "__main__":
    main()