from langchain.embeddings import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.chains import RetrievalQA
from langchain.vectorstores import Pinecone
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import TextLoader
from langchain.schema import Document
from typing import List, Dict, Any, Optional
import os
import logging
from dotenv import load_dotenv

from app.core.pinecone_client import pinecone_client

load_dotenv()
logger = logging.getLogger(__name__)

class RAGSystem:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        if not self.openai_api_key:
            logger.warning("OpenAI API key not found. RAG system will be disabled.")
            self.enabled = False
            return
        
        try:
            self.embeddings = OpenAIEmbeddings(openai_api_key=self.openai_api_key)
            self.llm = OpenAI(
                openai_api_key=self.openai_api_key,
                temperature=0.1,
                max_tokens=1000
            )
            
            # Initialize text splitter
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len
            )
            
            self.enabled = True
            logger.info("RAG system initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG system: {e}")
            self.enabled = False
    
    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings for a list of texts"""
        if not self.enabled:
            return []
        
        try:
            embeddings = self.embeddings.embed_documents(texts)
            return embeddings
        except Exception as e:
            logger.error(f"Failed to create embeddings: {e}")
            return []
    
    def create_query_embedding(self, query: str) -> List[float]:
        """Create embedding for a single query"""
        if not self.enabled:
            return []
        
        try:
            embedding = self.embeddings.embed_query(query)
            return embedding
        except Exception as e:
            logger.error(f"Failed to create query embedding: {e}")
            return []
    
    def process_documents(self, opportunities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process opportunities and create vector embeddings"""
        if not self.enabled or not pinecone_client.enabled:
            return []
        
        vectors = []
        texts = []
        
        for opp in opportunities:
            # Create text representation of opportunity
            text = f"""
            Título: {opp.get('title', '')}
            Descrição: {opp.get('description', '')}
            Categoria: {opp.get('category', '')}
            Tipo: {opp.get('type', '')}
            Região: {opp.get('region', '')}
            Valor: {opp.get('amount', '')}
            Fonte: {opp.get('source', '')}
            Tags: {', '.join(opp.get('tags', []))}
            """
            texts.append(text.strip())
        
        # Create embeddings
        embeddings = self.create_embeddings(texts)
        
        if not embeddings:
            return []
        
        # Prepare vectors for Pinecone
        for i, (opp, embedding) in enumerate(zip(opportunities, embeddings)):
            vector = {
                "id": f"opp_{opp['id']}",
                "values": embedding,
                "metadata": {
                    "title": opp.get('title', ''),
                    "category": opp.get('category', ''),
                    "type": opp.get('type', ''),
                    "region": opp.get('region', ''),
                    "amount": opp.get('amount', ''),
                    "source": opp.get('source', ''),
                    "opportunity_id": opp['id']
                }
            }
            vectors.append(vector)
        
        return vectors
    
    def semantic_search(
        self, 
        query: str, 
        filters: Optional[Dict[str, Any]] = None,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """Perform semantic search using RAG"""
        if not self.enabled or not pinecone_client.enabled:
            return []
        
        try:
            # Create query embedding
            query_embedding = self.create_query_embedding(query)
            if not query_embedding:
                return []
            
            # Search in Pinecone
            results = pinecone_client.query_vectors(
                vector=query_embedding,
                top_k=top_k,
                filter=filters
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to perform semantic search: {e}")
            return []
    
    def generate_response(
        self, 
        query: str, 
        context_docs: List[Dict[str, Any]]
    ) -> str:
        """Generate natural language response using retrieved context"""
        if not self.enabled:
            return "Sistema RAG não disponível no momento."
        
        try:
            # Prepare context from retrieved documents
            context = "\n\n".join([
                f"Oportunidade: {doc.get('metadata', {}).get('title', '')}\n"
                f"Categoria: {doc.get('metadata', {}).get('category', '')}\n"
                f"Tipo: {doc.get('metadata', {}).get('type', '')}\n"
                f"Região: {doc.get('metadata', {}).get('region', '')}\n"
                f"Valor: {doc.get('metadata', {}).get('amount', '')}"
                for doc in context_docs[:5]  # Limit context
            ])
            
            # Create prompt
            prompt = f"""
            Com base nas seguintes oportunidades de financiamento:

            {context}

            Responda à pergunta: {query}

            Forneça uma resposta detalhada e útil, incluindo informações específicas sobre as oportunidades mais relevantes.
            """
            
            # Generate response
            response = self.llm(prompt)
            return response.strip()
            
        except Exception as e:
            logger.error(f"Failed to generate response: {e}")
            return "Desculpe, não foi possível gerar uma resposta no momento."

# Global instance
rag_system = RAGSystem()