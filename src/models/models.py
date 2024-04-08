# Completion model
from models.ragtools import RAGServiceContext
from llama_index.core.extractors import SummaryExtractor
from llama_index.core.extractors import QuestionsAnsweredExtractor
from llama_index.extractors.entity import EntityExtractor
from llama_index.core.schema import MetadataMode
from llama_index.core.ingestion import IngestionPipeline

def generate_extractors(llm, device: str) -> list:
    # Metadata Extractors
    qa_extractor = QuestionsAnsweredExtractor(
        llm=llm, metadata_mode=MetadataMode.EMBED, questions=3
    )
    entity_extractor = EntityExtractor(
        device=device,
        prediction_threshold=0.5,
        label_entities=False,  # include the entity label in the metadata (can be erroneous)
    )
    summary_extractor = SummaryExtractor(summaries=["prev", "self", "next"], llm=llm)

    return qa_extractor, entity_extractor, summary_extractor

def embed_and_extract_metadata(documents: list, rag_service_context: RAGServiceContext, extractors: list):
    nodes = rag_service_context.text_splitter.get_nodes_from_documents(
      documents, show_progress=True
    )
    transforms = [rag_service_context.text_splitter, *extractors]
    pipeline = IngestionPipeline(transformations=transforms)
    metadata_nodes = pipeline.run(nodes=nodes, in_place=False, show_progress=True)
    return metadata_nodes
