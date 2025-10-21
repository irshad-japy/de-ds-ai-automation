from utils.qdrant_data_helper import RAG
from utils.schemas import Query
import time

def main(olalma_model, embedder_name):
    host = "localhost"
    rag = RAG(
        q_client_url=f"http://{host}:6333",
        q_api_key=None,                         # local http: no key
        ollama_base_url=f"http://{host}:11434",
        ollama_model=ollama_model,         # you have this; or "gemma:7b"
        embedder_name=embedder_name,  # must match ingestion
    )

    index = rag.qdrant_index(collection_name="roles_point_collection", chunk_size=1024)

    # make sure query character is not exceeding the model limit of 400
    jd = (
        "Design and deploy ML/GenAI systems. Strong Python. "
        "Experience with TensorFlow/PyTorch, MLOps, Git, CI/CD. "
        "Productionizing models, monitoring, and improvements."
    )
    q = Query(query=
            "You are an expert AI resume writer. Create 5–7 concise, ATS-friendly bullet points "
            "for Work Experience. Each bullet 70–90 characters, action-oriented, tech-specific, "
            "results-focused. Plain lines, newline-separated.\n\n"
            f"JOB TITLE: data engineer\n"
            f"JOB DESCRIPTION SNIPPET: {jd}\n"
        , similarity_top_k=5)
    res = rag.get_response(index=index, query=q, response_mode="compact", use_web_fallback=True)

    print("Result:", res.search_result)
    print("Source:", res.source)

if __name__ == "__main__":
    start = time.time()
    ollama_model = "llama3.2:3b-instruct-q4_K_M"
    embedder_name = "sentence-transformers/all-mpnet-base-v2"
    main(ollama_model, embedder_name)
    end = time.time()
    print(f"Elapsed time: {end - start:.2f} seconds")
