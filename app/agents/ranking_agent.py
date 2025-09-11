from crewai import Agent, Task, Crew
from langchain.tools import Tool
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

from app.core.langchain_rag import rag_system

logger = logging.getLogger(__name__)

class RankingAgent:
    def __init__(self):
        self.agent = Agent(
            role='Especialista em Ranqueamento',
            goal='Ranquear oportunidades de acordo com o perfil da startup',
            backstory="""Você é um especialista em matching de oportunidades de financiamento 
            com perfis de startups. Você analisa as características da startup (segmento, TRL, 
            área de atuação) e encontra as oportunidades mais relevantes.""",
            verbose=True,
            allow_delegation=False,
            tools=[
                Tool(
                    name="profile_matcher",
                    description="Calcula compatibilidade entre perfil e oportunidade",
                    func=self._calculate_profile_match
                ),
                Tool(
                    name="relevance_scorer",
                    description="Calcula score de relevância baseado em múltiplos fatores",
                    func=self._calculate_relevance_score
                )
            ]
        )
    
    def _calculate_profile_match(self, profile_data: str) -> str:
        """Calculate how well an opportunity matches a user profile"""
        try:
            # Parse profile data (simplified)
            lines = profile_data.split('\n')
            profile = {}
            opportunity = {}
            
            current_section = None
            for line in lines:
                line = line.strip()
                if line.startswith('PERFIL:'):
                    current_section = 'profile'
                elif line.startswith('OPORTUNIDADE:'):
                    current_section = 'opportunity'
                elif ':' in line and current_section:
                    key, value = line.split(':', 1)
                    if current_section == 'profile':
                        profile[key.strip().lower()] = value.strip()
                    else:
                        opportunity[key.strip().lower()] = value.strip()
            
            # Calculate match score
            score = 0
            max_score = 100
            
            # Category match (30 points)
            if profile.get('segmento', '').lower() in opportunity.get('categoria', '').lower():
                score += 30
            
            # Region match (20 points)
            profile_regions = profile.get('regiões preferidas', '').lower().split(',')
            opp_region = opportunity.get('região', '').lower()
            if any(region.strip() in opp_region for region in profile_regions):
                score += 20
            
            # TRL compatibility (25 points)
            try:
                profile_trl = int(profile.get('trl', 0))
                # Assume opportunity is suitable for TRL 4-9
                if 4 <= profile_trl <= 9:
                    score += 25
            except:
                pass
            
            # Amount compatibility (25 points)
            min_amount = profile.get('valor mínimo', '0')
            if min_amount and min_amount != '0':
                score += 15  # Partial score for having amount preference
            
            return f"Score de compatibilidade: {score}/{max_score} ({score/max_score*100:.1f}%)"
            
        except Exception as e:
            logger.error(f"Failed to calculate profile match: {e}")
            return "Erro no cálculo de compatibilidade"
    
    def _calculate_relevance_score(self, opportunity_data: str) -> str:
        """Calculate overall relevance score for an opportunity"""
        try:
            # Parse opportunity data
            lines = opportunity_data.split('\n')
            opp = {}
            
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    opp[key.strip().lower()] = value.strip()
            
            score = 50  # Base score
            
            # Recency bonus (up to 20 points)
            created_at = opp.get('criado em', '')
            if 'hoje' in created_at.lower() or 'ontem' in created_at.lower():
                score += 20
            elif 'semana' in created_at.lower():
                score += 10
            
            # Amount bonus (up to 15 points)
            amount = opp.get('valor', '').lower()
            if 'milhão' in amount or 'million' in amount:
                score += 15
            elif any(x in amount for x in ['mil', 'thousand', 'k']):
                score += 10
            
            # Source credibility (up to 15 points)
            source = opp.get('fonte', '').lower()
            credible_sources = ['finep', 'cnpq', 'fapesp', 'capes', 'união europeia']
            if any(s in source for s in credible_sources):
                score += 15
            
            # Ensure score is within bounds
            score = min(100, max(0, score))
            
            return f"Score de relevância: {score}/100"
            
        except Exception as e:
            logger.error(f"Failed to calculate relevance score: {e}")
            return "Score de relevância: 50/100"
    
    def rank_opportunities(
        self, 
        opportunities: List[Dict[str, Any]], 
        user_profile: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Rank opportunities based on user profile and other factors"""
        logger.info(f"Starting ranking of {len(opportunities)} opportunities...")
        
        if not user_profile:
            # Return opportunities with default scoring
            for opp in opportunities:
                opp['relevance_score'] = opp.get('relevance_score', 50.0)
            return sorted(opportunities, key=lambda x: x['relevance_score'], reverse=True)
        
        ranked_opportunities = []
        
        for opp in opportunities:
            try:
                # Prepare data for ranking
                profile_text = f"""
                PERFIL:
                Segmento: {user_profile.get('startup_segment', '')}
                TRL: {user_profile.get('startup_trl', '')}
                Área: {user_profile.get('startup_area', '')}
                Regiões Preferidas: {', '.join(user_profile.get('preferred_regions', []))}
                Categorias: {', '.join(user_profile.get('preferred_categories', []))}
                Valor Mínimo: {user_profile.get('min_amount', '')}
                
                OPORTUNIDADE:
                Título: {opp.get('title', '')}
                Categoria: {opp.get('category', '')}
                Tipo: {opp.get('type', '')}
                Região: {opp.get('region', '')}
                Valor: {opp.get('amount', '')}
                Fonte: {opp.get('source', '')}
                """
                
                # Create ranking task
                task = Task(
                    description=f"""
                    Analise a compatibilidade entre o perfil da startup e a oportunidade:
                    
                    {profile_text}
                    
                    Calcule um score de relevância considerando:
                    1. Compatibilidade de segmento/categoria
                    2. Adequação regional
                    3. Compatibilidade de TRL
                    4. Valor do financiamento
                    5. Credibilidade da fonte
                    6. Prazo de inscrição
                    
                    Forneça um score de 0 a 100 e justificativa.
                    """,
                    agent=self.agent
                )
                
                crew = Crew(
                    agents=[self.agent],
                    tasks=[task],
                    verbose=False
                )
                
                result = crew.kickoff()
                
                # Parse ranking result
                score = self._parse_ranking_result(str(result))
                
                # Update opportunity with ranking
                ranked_opp = opp.copy()
                ranked_opp['relevance_score'] = score
                ranked_opp['ranking_details'] = str(result)
                
                ranked_opportunities.append(ranked_opp)
                
            except Exception as e:
                logger.error(f"Failed to rank opportunity {opp.get('title', '')}: {e}")
                # Add with default score
                ranked_opp = opp.copy()
                ranked_opp['relevance_score'] = 50.0
                ranked_opportunities.append(ranked_opp)
        
        # Sort by relevance score
        ranked_opportunities.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        logger.info(f"Ranking completed for {len(ranked_opportunities)} opportunities")
        return ranked_opportunities
    
    def _parse_ranking_result(self, result: str) -> float:
        """Parse the ranking result to extract numerical score"""
        try:
            # Look for score patterns
            import re
            
            # Pattern: "score: 85/100" or "85 pontos" or "85%"
            patterns = [
                r'score[:\s]+(\d+)(?:/100)?',
                r'(\d+)\s*pontos',
                r'(\d+)%',
                r'relevância[:\s]+(\d+)'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, result.lower())
                if match:
                    score = float(match.group(1))
                    # Normalize to 0-100 if needed
                    if score > 100:
                        score = score / 10  # Assume it was out of 1000
                    return min(100.0, max(0.0, score))
            
            # If no pattern found, return default
            return 50.0
            
        except Exception as e:
            logger.error(f"Failed to parse ranking result: {e}")
            return 50.0
    
    def semantic_ranking(
        self, 
        query: str, 
        opportunities: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Rank opportunities using semantic similarity"""
        if not rag_system.enabled:
            return opportunities
        
        try:
            # Use RAG system for semantic search
            results = rag_system.semantic_search(query, top_k=len(opportunities))
            
            # Create mapping of opportunity IDs to semantic scores
            semantic_scores = {}
            for i, result in enumerate(results):
                opp_id = result.get('metadata', {}).get('opportunity_id')
                if opp_id:
                    # Higher rank = higher score (reverse index)
                    semantic_scores[opp_id] = (len(results) - i) / len(results) * 100
            
            # Update opportunities with semantic scores
            for opp in opportunities:
                opp_id = opp.get('id')
                if opp_id in semantic_scores:
                    # Combine existing relevance with semantic score
                    existing_score = opp.get('relevance_score', 50.0)
                    semantic_score = semantic_scores[opp_id]
                    # Weighted average: 60% semantic, 40% existing
                    opp['relevance_score'] = (semantic_score * 0.6) + (existing_score * 0.4)
            
            # Sort by updated scores
            opportunities.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
            
            return opportunities
            
        except Exception as e:
            logger.error(f"Failed to perform semantic ranking: {e}")
            return opportunities