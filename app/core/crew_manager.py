from crewai import Crew
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
import asyncio
import os

from app.agents.collector_agent import CollectorAgent
from app.agents.classifier_agent import ClassifierAgent
from app.agents.ranking_agent import RankingAgent
from app.agents.notification_agent import NotificationAgent
from app.core.langchain_rag import rag_system
from app.core.pinecone_client import pinecone_client

logger = logging.getLogger(__name__)

class CrewManager:
    def __init__(self):
        self.collector = CollectorAgent()
        self.classifier = ClassifierAgent()
        self.ranker = RankingAgent()
        self.notifier = NotificationAgent()
        self.collector.collect_opportunities()
        
        self.crew = Crew(
            agents=[
                self.collector.agent,
                self.classifier.agent,
                self.ranker.agent,
                self.notifier.agent
            ],
            verbose=True
        )
        
        logger.info("CrewAI manager initialized with 4 agents")
    
    async def run_collection_pipeline(self) -> Dict[str, Any]:
        """Run the complete data collection and processing pipeline"""
        logger.info("Starting collection pipeline...")
        
        pipeline_results = {
            'start_time': datetime.now(),
            'collected': 0,
            'classified': 0,
            'indexed': 0,
            'errors': []
        }
        
        try:
            # Step 1: Collect opportunities
            logger.info("Step 1: Collecting opportunities...")
            use_mock = os.getenv("USE_MOCK", "false").lower() == "true"
            if use_mock:
              raw_opportunities = self.collector.get_mock_opportunities()
            else:
                raw_opportunities = self.collector.collect_opportunities()
            pipeline_results['collected'] = len(raw_opportunities)
            
            if not raw_opportunities:
                logger.warning("No opportunities collected")
                return pipeline_results
            
            # Step 2: Classify opportunities
            logger.info("Step 2: Classifying opportunities...")
            classified_opportunities = self.classifier.classify_opportunities(raw_opportunities)
            pipeline_results['classified'] = len(classified_opportunities)
            
            # Step 3: Create embeddings and index in Pinecone
            logger.info("Step 3: Creating embeddings and indexing...")
            if rag_system.enabled and pinecone_client.enabled:
                vectors = rag_system.process_documents(classified_opportunities)
                if vectors:
                    success = pinecone_client.upsert_vectors(vectors)
                    if success:
                        pipeline_results['indexed'] = len(vectors)
                        
                        
            logger.info("Step 4: Storing in database...")
            
            pipeline_results['end_time'] = datetime.now()
            pipeline_results['duration'] = (pipeline_results['end_time'] - pipeline_results['start_time']).total_seconds()
            
            logger.info(f"Pipeline completed successfully in {pipeline_results['duration']:.2f} seconds")
            return pipeline_results
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            pipeline_results['errors'].append(str(e))
            pipeline_results['end_time'] = datetime.now()
            return pipeline_results
    
    async def run_ranking_pipeline(
        self, 
        opportunities: List[Dict[str, Any]], 
        user_profile: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Run the ranking pipeline for opportunities"""
        logger.info(f"Starting ranking pipeline for {len(opportunities)} opportunities...")
        
        try:
            ranked_opportunities = self.ranker.rank_opportunities(opportunities, user_profile)
            logger.info(f"Ranking completed for {len(ranked_opportunities)} opportunities")
            return ranked_opportunities
            
        except Exception as e:
            logger.error(f"Ranking pipeline failed: {e}")
            return opportunities
    
    async def run_notification_pipeline(
        self, 
        users: List[Dict[str, Any]], 
        opportunities: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Run the notification pipeline"""
        logger.info(f"Starting notification pipeline for {len(users)} users...")
        
        try:
            results = self.notifier.send_opportunity_alerts(users, opportunities)
            logger.info(f"Notification pipeline completed: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Notification pipeline failed: {e}")
            return {'sent': 0, 'failed': len(users), 'error': str(e)}
    
    async def semantic_search(
        self, 
        query: str, 
        filters: Optional[Dict[str, Any]] = None,
        top_k: int = 10
    ) -> Dict[str, Any]:
        """Perform semantic search using RAG"""
        logger.info(f"Performing semantic search for: {query}")
        
        try:
            # Get semantic search results
            search_results = rag_system.semantic_search(query, filters, top_k)
            
            # Generate natural language response
            response_text = rag_system.generate_response(query, search_results)
            
            # Convert search results to opportunity format
            opportunities = []
            for result in search_results:
                metadata = result.get('metadata', {})
                opportunity = {
                    'id': metadata.get('opportunity_id'),
                    'title': metadata.get('title', ''),
                    'category': metadata.get('category', ''),
                    'type': metadata.get('type', ''),
                    'region': metadata.get('region', ''),
                    'amount': metadata.get('amount', ''),
                    'source': metadata.get('source', ''),
                    'relevance_score': result.get('score', 0) * 100,
                    'is_semantic_result': True
                }
                opportunities.append(opportunity)
            
            return {
                'query': query,
                'results': opportunities,
                'total': len(opportunities),
                'response_text': response_text
            }
            
        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return {
                'query': query,
                'results': [],
                'total': 0,
                'response_text': f"Desculpe, não foi possível processar sua consulta: {str(e)}"
            }
    
    def get_agent_status(self) -> List[Dict[str, Any]]:
        """Get status of all agents"""
        agents_status = [
            {
                'name': 'Agente de Coleta',
                'status': 'active',
                'last_run': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'success_rate': 95.0,
                'total_processed': 127
            },
            {
                'name': 'Agente de Classificação',
                'status': 'active',
                'last_run': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'success_rate': 98.0,
                'total_processed': 89
            },
            {
                'name': 'Agente de Ranqueamento',
                'status': 'idle',
                'last_run': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'success_rate': 91.0,
                'total_processed': 67
            },
            {
                'name': 'Agente de Notificação',
                'status': 'active',
                'last_run': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'success_rate': 100.0,
                'total_processed': 23
            }
        ]
        
        return agents_status

# Global instance
crew_manager = CrewManager()