import os
from dotenv import load_dotenv

load_dotenv()


def test_llm():
    from langchain_google_genai import ChatGoogleGenerativeAI
    llm = ChatGoogleGenerativeAI(model=os.getenv("GEMINI_MODEL"), temperature=0)
    resp = llm.invoke("In one sentence, what is a payment aggregator?")
    print("LLM OK:", resp.content)


def test_embeddings():
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("BAAI/bge-small-en-v1.5")
    vecs = model.encode(["digital lending cooling-off period", "KYC for merchants"],
                        normalize_embeddings=True)
    print("Embeddings OK, shape:", vecs.shape)


if __name__ == "__main__":
    test_embeddings()
    test_llm()