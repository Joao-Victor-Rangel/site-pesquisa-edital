from typing import List, Dict, Any, Optional
import logging
import re
from datetime import datetime
from langchain.tools import BaseTool

from app.core.langchain_rag import rag_system

logger = logging.getLogger(__name__)


class ProfileMatcherTool(BaseTool):
    name = "profile_matcher"
    description = "Calcula compatibilidade entre perfil e oportunidade"

    def _run(self, profile_data: str) -> str:
        try:
            # Parse profile data
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

            score = 0
            max_score = 100

            if profile.get('segmento', '').lower() in opportunity.get('categoria', '').lower():
                score += 30

            profile_regions = profile.get('regiões preferidas', '').lower().split(',')
            opp_region = opportunity.get('região', '').lower()
            if any(region.strip() in opp_region for region in profile_regions):
                score += 20

            try:
                profile_trl = int(profile.get('trl', 0))
                if 4 <= profile_trl <= 9:
                    score += 25
            except:
                pass

            min_amount = profile.get('valor mínimo', '0')
            if min_amount and min_amount != '0':
                score += 15

            return f"Score de compatibilidade: {score}/{max_score} ({score/max_score*100:.1f}%)"

        except Exception as e:
            logger.error(f"Failed to calculate profile match: {e}")
            return "Erro no cálculo de compatibilidade"

    def _arun(self, *args, **kwargs):
        raise NotImplementedError("Somente execução síncrona suportada.")


class RelevanceScorerTool(BaseTool):
    name = "relevance_scorer"
    description = "Calcula score de relevância baseado em múltiplos fatores"

    def _run(self, opportunity_data: str) -> str:
        try:
            lines = opportunity_data.split('\n')
            opp = {}

            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    opp[key.strip().lower()] = value.strip()

            score = 50

            created_at = opp.get('criado em', '')
            if 'hoje' in created_at.lower() or 'ontem' in created_at.lower():
                score += 20
            elif 'semana' in created_at.lower():
                score += 10

            amount = opp.get('valor', '').lower()
            if 'milhão' in amount or 'million' in amount:
                score += 15
            elif any(x in amount for x in ['mil', 'thousand', 'k']):
                score += 10

            source = opp.get('fonte', '').lower()
            credible_sources = ['finep', 'cnpq', 'fapesp', 'capes', 'união europeia']
            if any(s in source for s in credible_sources):
                score += 15

            score = min(100, max(0, score))
            return f"Score de relevância: {score}/100"

        except Exception as e:
            logger.error(f"Failed to calculate relevance score: {e}")
            return "Score de relevância: 50/100"

    def _arun(self, *args, **kwargs):
        raise NotImplementedError("Somente execução síncrona suportada.")


class RankingAgent:
    def __init__(self):
        self.profile_matcher = ProfileMatcherTool()
        self.relevance_scorer = RelevanceScorerTool()

    def rank_opportunities(
        self,
        opportunities: List[Dict[str, Any]],
        user_profile: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        logger.info(f"Starting ranking of {len(opportunities)} opportunities...")

        if not user_profile:
            for opp in opportunities:
                opp['relevance_score'] = opp.get('relevance_score', 50.0)
            return sorted(opportunities, key=lambda x: x['relevance_score'], reverse=True)

        ranked_opportunities = []
        for opp in opportunities:
            try:
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

                profile_result = self.profile_matcher.run(profile_text)
                relevance_result = self.relevance_scorer.run(profile_text)

                score = self._parse_ranking_result(profile_result + " " + relevance_result)

                ranked_opp = opp.copy()
                ranked_opp['relevance_score'] = score
                ranked_opp['ranking_details'] = {
                    "profile_match": profile_result,
                    "relevance_score": relevance_result,
                }

                ranked_opportunities.append(ranked_opp)

            except Exception as e:
                logger.error(f"Failed to rank opportunity {opp.get('title', '')}: {e}")
                ranked_opp = opp.copy()
                ranked_opp['relevance_score'] = 50.0
                ranked_opportunities.append(ranked_opp)

        ranked_opportunities.sort(key=lambda x: x['relevance_score'], reverse=True)
        logger.info(f"Ranking completed for {len(ranked_opportunities)} opportunities")
        return ranked_opportunities

    def _parse_ranking_result(self, result: str) -> float:
        try:
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
                    if score > 100:
                        score = score / 10
                    return min(100.0, max(0.0, score))
            return 50.0
        except Exception as e:
            logger.error(f"Failed to parse ranking result: {e}")
            return 50.0

    def semantic_ranking(
        self,
        query: str,
        opportunities: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        if not rag_system.enabled:
            return opportunities
        try:
            results = rag_system.semantic_search(query, top_k=len(opportunities))
            semantic_scores = {
                result.get('metadata', {}).get('opportunity_id'): (len(results) - i) / len(results) * 100
                for i, result in enumerate(results)
            }

            for opp in opportunities:
                opp_id = opp.get('id')
                if opp_id in semantic_scores:
                    existing_score = opp.get('relevance_score', 50.0)
                    semantic_score = semantic_scores[opp_id]
                    opp['relevance_score'] = (semantic_score * 0.6) + (existing_score * 0.4)

            opportunities.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
            return opportunities
        except Exception as e:
            logger.error(f"Failed to perform semantic ranking: {e}")
            return opportunities
