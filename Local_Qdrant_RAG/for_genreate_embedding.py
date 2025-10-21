from utils import qdrant_data_helper

def ingest_data(data_path, collection_name, embedder_name):
    """Ingest data from the specified folder into Qdrant."""
    ingestor = qdrant_data_helper.DataIngestor(
        q_client_url="http://localhost:6333/", 
        q_api_key=None, # you can change this to your own qdrant api key if you have set it, otherwise, using None
        data_path=data_path,        # "./data/roles_point", 
        collection_name=collection_name,    # "roles_point_collection",
        embedder_name=embedder_name, # "sentence-transformers/all-mpnet-base-v2",
        chunk_size=100
        )

    index = ingestor.ingest()

    print("Index created successfully!")
    
if __name__ == "__main__":
    data_path = "./data/roles_point"
    collection_name="roles_point_collection",
    embedder_name="sentence-transformers/all-mpnet-base-v2"
    ingest_data(data_path, collection_name, embedder_name)