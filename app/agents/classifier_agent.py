from crewai import Agent, Task, Crew
from langchain.tools import BaseTool
from typing import List, Dict, Any
import logging
import re

logger = logging.getLogger(__name__)


# 🔹 Tool 1: Classificação de texto
class TextClassifierTool(BaseTool):
    name = "text_classifier"
    description = "Classifica texto por categoria e tipo"

    def _run(self, text: str) -> str:
        text_lower = text.lower()

        categories = {
            'Inteligência Artificial': ['ia', 'artificial intelligence', 'machine learning', 'deep learning', 'ai'],
            'Saúde': ['saúde', 'health', 'medicina', 'medical', 'biotecnologia', 'biotech'],
            'Energia': ['energia', 'energy', 'sustentabilidade', 'renewable', 'solar', 'eólica'],
            'Fintech': ['fintech', 'financeiro', 'financial', 'blockchain', 'crypto'],
            'Agtech': ['agtech', 'agricultura', 'agriculture', 'agronegócio', 'farming'],
            'Educação': ['educação', 'education', 'edtech', 'ensino', 'learning'],
            'Mobilidade': ['mobilidade', 'mobility', 'transporte', 'transport', 'logística'],
            'Indústria 4.0': ['indústria', 'industry', 'manufatura', 'iot', 'automação']
        }

        types = {
            'edital': ['edital', 'chamada pública', 'concurso', 'seleção pública'],
            'bolsa': ['bolsa', 'scholarship', 'fellowship', 'auxílio'],
            'investimento': ['investimento', 'investment', 'funding', 'capital', 'venture']
        }

        # Categoria
        category_scores = {cat: sum(1 for kw in kws if kw in text_lower) for cat, kws in categories.items()}
        best_category = max(category_scores, key=category_scores.get) if any(category_scores.values()) else "Geral"

        # Tipo
        type_scores = {tp: sum(1 for kw in kws if kw in text_lower) for tp, kws in types.items()}
        best_type = max(type_scores, key=type_scores.get) if any(type_scores.values()) else "edital"

        return f"Categoria: {best_category}, Tipo: {best_type}"

    async def _arun(self, text: str) -> str:
        raise NotImplementedError("Execução assíncrona não implementada.")


# 🔹 Tool 2: Extração de palavras-chave
class KeywordExtractorTool(BaseTool):
    name = "extract_keywords"
    description = "Extrai palavras-chave relevantes do texto"

    def _run(self, text: str) -> str:
        text_lower = text.lower()

        funding_keywords = [
            'financiamento', 'bolsa', 'edital', 'investimento', 'startup', 'inovação',
            'pesquisa', 'desenvolvimento', 'tecnologia', 'ciência', 'empreendedorismo'
        ]

        found_keywords = [kw for kw in funding_keywords if kw in text_lower]

        amounts = re.findall(r'r\$\s*[\d.,]+', text_lower)
        dates = re.findall(r'\d{1,2}/\d{1,2}/\d{4}', text)

        return str({
            "keywords": found_keywords,
            "amounts": amounts,
            "dates": dates
        })

    async def _arun(self, text: str) -> str:
        raise NotImplementedError("Execução assíncrona não implementada.")


# 🔹 ClassifierAgent usando BaseTool
class ClassifierAgent:
    def __init__(self):
        self.agent = Agent(
            role="Classificador de Oportunidades",
            goal="Classificar oportunidades por categoria, tipo e relevância",
            backstory=(
                "Você é um especialista em categorização de oportunidades de financiamento. "
                "Você analisa o conteúdo de editais e oportunidades para classificá-las adequadamente "
                "por área de conhecimento, tipo de financiamento e outros critérios relevantes."
            ),
            verbose=True,
            allow_delegation=False,
            tools=[TextClassifierTool(), KeywordExtractorTool()]
        )

    def classify_opportunities(self, opportunities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        logger.info(f"Starting classification of {len(opportunities)} opportunities...")

        classified_opportunities = []

        for opp in opportunities:
            try:
                text_content = f"{opp.get('title', '')} {opp.get('description', '')}"

                task = Task(
                    description=f"""
                    Analise o seguinte conteúdo e classifique a oportunidade:

                    Título: {opp.get('title', '')}
                    Descrição: {opp.get('description', '')}

                    Determine:
                    1. Categoria principal (área de conhecimento)
                    2. Tipo de oportunidade (edital, bolsa, investimento)
                    3. Palavras-chave relevantes
                    4. Nível de relevância (1-10)

                    Forneça uma classificação estruturada.
                    """,
                    agent=self.agent
                )

                crew = Crew(
                    agents=[self.agent],
                    tasks=[task],
                    verbose=False
                )

                result = crew.kickoff()

                classification = self._parse_classification_result(str(result))

                classified_opp = opp.copy()
                classified_opp.update({
                    "category": classification.get("category", "Geral"),
                    "type": classification.get("type", "edital"),
                    "tags": classification.get("keywords", []),
                    "relevance_score": classification.get("relevance", 50.0)
                })

                classified_opportunities.append(classified_opp)

            except Exception as e:
                logger.error(f"Failed to classify opportunity {opp.get('title', '')}: {e}")
                classified_opp = opp.copy()
                classified_opp.update({
                    "category": "Geral",
                    "type": "edital",
                    "tags": [],
                    "relevance_score": 50.0
                })
                classified_opportunities.append(classified_opp)

        logger.info(f"Classification completed for {len(classified_opportunities)} opportunities")
        return classified_opportunities

    def _parse_classification_result(self, result: str) -> Dict[str, Any]:
        result_lower = result.lower()

        categories = [
            'Inteligência Artificial', 'Saúde', 'Energia', 'Fintech',
            'Agtech', 'Educação', 'Mobilidade', 'Indústria 4.0'
        ]
        category = next((c for c in categories if c.lower() in result_lower), "Geral")

        types = ["edital", "bolsa", "investimento"]
        opp_type = next((t for t in types if t in result_lower), "edital")

        keywords = [kw for kw in ["ia", "saúde", "energia", "fintech", "agtech", "educação", "mobilidade", "indústria"]
                    if kw in result_lower]

        relevance = 70.0 if keywords else 50.0

        return {
            "category": category,
            "type": opp_type,
            "keywords": keywords[:5],
            "relevance": relevance
        }
