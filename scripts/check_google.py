import os
import sys

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

try:
    # Ensure project root is on path
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    if project_root not in sys.path:
        sys.path.append(project_root)
    # Force provider to google for this check
    os.environ["LLM_PROVIDER"] = "google"
    from services.ai_suggestions import AISuggestionEngine
except Exception as e:
    print("GOOGLE IMPORT ERROR:", type(e).__name__, str(e))
    sys.exit(1)

def main():
    key = os.getenv("GOOGLE_API_KEY")
    print("Key present:", bool(key))
    if not key:
        print("CONNECTED:", False)
        return

    try:
        eng = AISuggestionEngine()
        llm = eng.llm
        print("LLM class:", type(llm).__name__ if llm else None)
        if llm is None:
            print("CONNECTED:", False)
            return
        resp = llm.invoke("Hello")
        ok = bool(resp and getattr(resp, "content", None))
        print("Google call succeeded:", ok)
        print("CONNECTED:", ok)
    except Exception as e:
        print("Google call error:", type(e).__name__, str(e)[:500])
        print("CONNECTED:", False)

if __name__ == "__main__":
    main()