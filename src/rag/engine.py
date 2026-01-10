import logging
import json
from typing import Dict, Any, List

from mathesis_core.db.chroma import ChromaHybridStore
from mathesis_core.llm.clients import OllamaClient
from .parser import PDFTableParser
from .chunker import SectionChunker

logger = logging.getLogger(__name__)

class RAGEngine:
    """
    Orchestrates the RAG pipeline: Ingestion -> Storage -> Retrieval -> Generation.
    """
    
    def __init__(self, collection_name: str = "school_info_v1"):
        # Initialize Common Components
        self.ollama = OllamaClient(base_url="http://localhost:11434")
        self.vector_store = ChromaHybridStore(
            collection_name=collection_name, 
            ollama_client=self.ollama,
            persist_dir="./chroma_db"
        )
        
        # Initialize Node-Specific Components
        self.parser = PDFTableParser()
        self.chunker = SectionChunker()
        
    def ingest_file(self, file_path: str, metadata: Dict[str, Any] = None) -> int:
        """
        Parses and indexes a file. Returns number of chunks indexed.
        """
        logger.info(f"Ingesting file: {file_path}")
        if metadata is None:
            metadata = {}
            
        # 1. Parse
        markdown_text = self.parser.parse(file_path)
        if not markdown_text:
            logger.warning("Empty text parsed.")
            return 0
            
        # 2. Chunk
        chunks = self.chunker.chunk(markdown_text)
        
        # 3. Store
        texts = [c["text"] for c in chunks]
        metadatas = []
        for c in chunks:
            # Merge global metadata with chunk metadata
            meta = metadata.copy()
            meta.update(c["metadata"])
            # Flatten metadata? Chroma requires string/int/float/bool
            # Ensure safe types
            safe_meta = {k: str(v) for k, v in meta.items()}
            metadatas.append(safe_meta)
            
        self.vector_store.add_documents(texts, metadatas)
        logger.info(f"Indexed {len(texts)} chunks.")
        return len(texts)

    def query(self, question: str, k: int = 4) -> Dict[str, Any]:
        """
        Answers a user query using RAG and returns structured JSON.
        """
        # 1. Retrieve
        retrieved_docs = self.vector_store.hybrid_search(question, k=k)
        
        # 2. Construct Context
        context_str = "\n\n---\n\n".join([f"[Source: {d.get('metadata', {}).get('header', 'Unknown')}]\n{d['text']}" for d in retrieved_docs])
        
        # 3. Generate Answer (Structured)
        system_prompt = (
            "You are an expert education data analyst. "
            "Analyze the provided context from school documents and answer the user's question. "
            "You MUST output the response in valid JSON format with the following keys:\n"
            "- answer: A clear, summarized answer in Korean.\n"
            "- references: A list of specific sections or tables used.\n"
            "- details: A structured object containing key statistics or facts found.\n"
            "If the answer is not found in the context, state that data is missing in the 'answer' field."
        )
        
        full_prompt = f"""Context:\n{context_str}\n\nQuestion: {question}"""
        
        try:
            response_text = self.ollama.generate(
                prompt=full_prompt, 
                system=system_prompt,
                format="json", # Force JSON mode if model supports
                temperature=0.1
            )
            
            # Parse JSON safely
            try:
                response_json = json.loads(response_text)
            except json.JSONDecodeError:
                # Fallback if model failed pure JSON
                response_json = {
                    "answer": response_text,
                    "references": [],
                    "details": {},
                    "error": "JSON parsing failed"
                }
                
            # Augment with retrieval info
            response_json["retrieved_chunks"] = [d['text'][:50] + "..." for d in retrieved_docs]
            
            return response_json
            
        except Exception as e:
            logger.error(f"RAG Generation failed: {e}")
            return {"error": str(e)}
