from pymilvus import connections, Collection
from loguru import logger

def search_vector_db(query_vector, collection_name="financial_docs", top_k=3):
    connections.connect("default", host="milvus", port="19530")
    collection = Collection(collection_name)
    results = collection.search(
        data=[query_vector],
        anns_field="embedding",
        param={"metric_type": "IP", "params": {"nprobe": 10}},
        limit=top_k,
        output_fields=["title", "content"]
    )
    matches = []
    for hit in results[0]:
        matches.append(hit.entity.get("content"))
    logger.info(f"RAG 搜尋結果 {len(matches)} 筆")
    return "\n".join(matches)
