# Helper Functions for Medium API Ingestion
import weaviate
from llama_index.core import ServiceContext
from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.weaviate import WeaviateVectorStore

def get_weaviate_vector_store(client: weaviate.Client, index_name: str) -> WeaviateVectorStore:
  vector_store = WeaviateVectorStore(weaviate_client=client, index_name=index_name)
  return vector_store


def get_index_from_weaviate_vector_store(vector_store: WeaviateVectorStore, service_context: ServiceContext) -> VectorStoreIndex:
    index = VectorStoreIndex.from_vector_store(
      vector_store=vector_store, service_context=service_context)
    return index


def refresh_weaviate_index(documents: list, index: VectorStoreIndex) -> bool:
   try:
    index.refresh_ref_docs(documents)
    status = True
   except Exception:
    status = False
   finally:
     return status
   