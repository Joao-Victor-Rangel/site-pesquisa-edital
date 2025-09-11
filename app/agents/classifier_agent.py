from crewai import Agent, Task, Crew
from langchain.tools import Tool
from typing import List, Dict, Any
import logging
import re

logger = logging.getLogger(__name__)

class ClassifierAgent:
    def __init__(self):
        self.categories = {
            'Inteligência Artificial': ['ia', 'artificial intelligence', 'machine learning', 'deep learning', 'ai'],
            'Saúde': ['saúde', 'health', 'medicina', 'medical', 'biotecnologia', 'biotech'],
            'Energia': ['energia', 'energy', 'sustentabilidade', 'renewable', 'solar', 'eólica'],
            'Fintech': ['fintech', 'financeiro', 'financial', 'blockchain', 'crypto'],
            'Agtech': ['agtech', 'agricultura', 'agriculture', 'agronegócio', 'farming'],
            'Educação': ['educação', 'education', 'edtech', 'ensino', 'learning'],
            'Mobilidade': ['mobilidade', 'mobility', 'transporte', 'transport', 'logística'],
            'Indústria 4.0': ['indústria', 'industry', 'manufatura', 'iot', 'automação']
        }
        
        self.types = {
            'edital': ['edital', 'chamada pública', 'concurso', 'seleção pública'],
            'bolsa': ['bolsa', 'scholarship', 'fellowship', 'auxílio'],
            'investimento': ['investimento', 'investment', 'funding', 'capital', 'venture']
        }
        
        self.agent = Agent(
            role='Classificador de Oportunidades',
            goal='Classificar oportunidades por categoria, tipo e relevância',
            backstory="""Você é um especialista em categorização de oportunidades de financiamento. 
            Você analisa o conteúdo de editais e oportunidades para classificá-las adequadamente 
            por área de conhecimento, tipo de financiamento e outros critérios relevantes.""",
            verbose=True,
            allow_delegation=False,
            tools=[
                Tool(
                    name="text_classifier",
                    description="Classifica texto por categoria e tipo",
                    func=self._classify_text
                ),
                Tool(
                    name="extract_keywords",
                    description="Extrai palavras-chave relevantes do texto",
                    func=self._extract_keywords
                )
            ]
        )
    
    def _classify_text(self, text: str) -> str:
        """Classify text into categories and types"""
        text_lower = text.lower()
        
        # Classify category
        category_scores = {}
        for category, keywords in self.categories.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                category_scores[category] = score
        
        best_category = max(category_scores.items(), key=lambda x: x[1])[0] if category_scores else 'Geral'
        
        # Classify type
        type_scores = {}
        for type_name, keywords in self.types.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                type_scores[type_name] = score
        
        best_type = max(type_scores.items(), key=lambda x: x[1])[0] if type_scores else 'edital'
        
        return f"Categoria: {best_category}, Tipo: {best_type}"
    
    def _extract_keywords(self, text: str) -> str:
        """Extract relevant keywords from text"""
        # Simple keyword extraction - in production, use more sophisticated NLP
        text_lower = text.lower()
        
        # Common funding-related keywords
        funding_keywords = [
            'financiamento', 'bolsa', 'edital', 'investimento', 'startup', 'inovação',
            'pesquisa', 'desenvolvimento', 'tecnologia', 'ciência', 'empreendedorismo'
        ]
        
        found_keywords = [keyword for keyword in funding_keywords if keyword in text_lower]
        
        # Extract amounts
        amount_pattern = r'r\$\s*[\d.,]+'
        amounts = re.findall(amount_pattern, text_lower)
        
        # Extract dates
        date_pattern = r'\d{1,2}/\d{1,2}/\d{4}'
        dates = re.findall(date_pattern, text)
        
        result = {
            'keywords': found_keywords,
            'amounts': amounts,
            'dates': dates
        }
        
        return str(result)
    
    def classify_opportunities(self, opportunities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Classify a list of opportunities"""
        logger.info(f"Starting classification of {len(opportunities)} opportunities...")
        
        classified_opportunities = []
        
        for opp in opportunities:
            try:
                # Prepare text for classification
                text_content = f"{opp.get('title', '')} {opp.get('description', '')}"
                
                # Create classification task
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
                
                # Parse classification result
                classification = self._parse_classification_result(str(result))
                
                # Update opportunity with classification
                classified_opp = opp.copy()
                classified_opp.update({
                    'category': classification.get('category', 'Geral'),
                    'type': classification.get('type', 'edital'),
                    'tags': classification.get('keywords', []),
                    'relevance_score': classification.get('relevance', 50.0)
                })
                
                classified_opportunities.append(classified_opp)
                
            except Exception as e:
                logger.error(f"Failed to classify opportunity {opp.get('title', '')}: {e}")
                # Add with default classification
                classified_opp = opp.copy()
                classified_opp.update({
                    'category': 'Geral',
                    'type': 'edital',
                    'tags': [],
                    'relevance_score': 50.0
                })
                classified_opportunities.append(classified_opp)
        
        logger.info(f"Classification completed for {len(classified_opportunities)} opportunities")
        return classified_opportunities
    
    def _parse_classification_result(self, result: str) -> Dict[str, Any]:
        """Parse the classification result from the agent"""
        # Simple parsing - in production, use more structured output
        result_lower = result.lower()
        
        # Extract category
        category = 'Geral'
        for cat in self.categories.keys():
            if cat.lower() in result_lower:
                category = cat
                break
        
        # Extract type
        opp_type = 'edital'
        for t in self.types.keys():
            if t in result_lower:
                opp_type = t
                break
        
        # Extract keywords (simplified)
        keywords = []
        for cat_keywords in self.categories.values():
            for keyword in cat_keywords:
                if keyword in result_lower:
                    keywords.append(keyword)
        
        # Simple relevance scoring
        relevance = 70.0 if keywords else 50.0
        
        return {
            'category': category,
            'type': opp_type,
            'keywords': list(set(keywords))[:5],  # Limit to 5 unique keywords
            'relevance': relevance
        }