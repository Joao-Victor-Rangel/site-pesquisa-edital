from crewai import Agent, Task, Crew
from langchain.tools import Tool
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
import logging
from datetime import datetime, timedelta
import re

logger = logging.getLogger(__name__)

class CollectorAgent:
    def __init__(self):
        self.sources = {
            "finep": "https://www.finep.gov.br/chamadas-publicas",
            "cnpq": "https://www.gov.br/cnpq/pt-br/acesso-a-informacao/acoes-e-programas/programas",
            "fapesp": "https://fapesp.br/oportunidades/",
            "capes": "https://www.gov.br/capes/pt-br/acesso-a-informacao/acoes-e-programas",
        }
        
        self.agent = Agent(
            role='Coletor de Oportunidades',
            goal='Coletar informações sobre editais, bolsas e oportunidades de financiamento',
            backstory="""Você é um especialista em encontrar oportunidades de financiamento 
            para startups e pesquisadores. Você monitora constantemente sites governamentais, 
            agências de fomento e outras fontes relevantes.""",
            verbose=True,
            allow_delegation=False,
            tools=[
                Tool(
                    name="web_scraper",
                    description="Extrai informações de páginas web",
                    func=self._scrape_website
                ),
                Tool(
                    name="content_parser",
                    description="Analisa e extrai dados estruturados de conteúdo HTML",
                    func=self._parse_content
                )
            ]
        )
    
    def _scrape_website(self, url: str) -> str:
        """Scrape website content"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text content
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text[:5000]  # Limit content size
            
        except Exception as e:
            logger.error(f"Failed to scrape {url}: {e}")
            return f"Erro ao acessar {url}: {str(e)}"
    
    def _parse_content(self, content: str) -> str:
        """Parse content and extract structured information"""
        try:
            # Simple parsing logic - in production, use more sophisticated NLP
            opportunities = []
            
            # Look for common patterns in funding announcements
            patterns = [
                r'edital\s+n[º°]?\s*(\d+/\d+)',
                r'chamada\s+pública\s+n[º°]?\s*(\d+/\d+)',
                r'bolsa\s+de\s+(\w+)',
                r'financiamento\s+de\s+até\s+r\$\s*([\d.,]+)',
                r'prazo\s+até\s+(\d{1,2}/\d{1,2}/\d{4})',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    opportunities.extend(matches)
            
            return f"Encontradas {len(opportunities)} possíveis oportunidades: {opportunities[:10]}"
            
        except Exception as e:
            logger.error(f"Failed to parse content: {e}")
            return "Erro ao processar conteúdo"
    
    def collect_opportunities(self) -> List[Dict[str, Any]]:
        """Main collection method"""
        logger.info("Starting opportunity collection...")
        
        collected_data = []
        
        for source_name, source_url in self.sources.items():
            try:
                logger.info(f"Collecting from {source_name}: {source_url}")
                
                task = Task(
                    description=f"""
                    Acesse o site {source_url} e colete informações sobre:
                    1. Editais abertos
                    2. Bolsas disponíveis
                    3. Oportunidades de financiamento
                    4. Prazos e valores
                    5. Requisitos básicos
                    
                    Extraia dados estruturados e organize as informações.
                    """,
                    agent=self.agent
                )
                
                crew = Crew(
                    agents=[self.agent],
                    tasks=[task],
                    verbose=True
                )
                
                result = crew.kickoff()
                
                # Process result and create opportunity objects
                opportunity = {
                    'external_id': f"{source_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    'title': f"Oportunidades coletadas de {source_name.upper()}",
                    'description': str(result),
                    'source': source_name,
                    'source_url': source_url,
                    'category': 'Geral',
                    'type': 'edital',
                    'region': 'Brasil',
                    'collected_at': datetime.now(),
                    'tags': [source_name, 'coletado_automaticamente']
                }
                
                collected_data.append(opportunity)
                
            except Exception as e:
                logger.error(f"Failed to collect from {source_name}: {e}")
                continue
        
        logger.info(f"Collection completed. Found {len(collected_data)} opportunities")
        return collected_data
    
    def get_mock_opportunities(self) -> List[Dict[str, Any]]:
        """Generate mock opportunities for testing"""
        mock_data = [
            {
                'external_id': 'finep_2024_001',
                'title': 'FINEP - Subvenção Econômica para Startups de IA',
                'description': 'Programa de apoio financeiro para startups desenvolvedoras de soluções de inteligência artificial com foco em impacto social.',
                'category': 'Inteligência Artificial',
                'type': 'edital',
                'region': 'Brasil',
                'deadline': datetime.now() + timedelta(days=45),
                'amount': 'R$ 500.000',
                'source': 'FINEP',
                'source_url': 'https://www.finep.gov.br/chamadas-publicas',
                'tags': ['IA', 'Startup', 'Inovação', 'Subvenção'],
                'collected_at': datetime.now()
            },
            {
                'external_id': 'cnpq_2024_002',
                'title': 'CNPq - Bolsa de Desenvolvimento Tecnológico',
                'description': 'Bolsa para desenvolvimento de tecnologias disruptivas em healthtech com duração de 24 meses.',
                'category': 'Saúde',
                'type': 'bolsa',
                'region': 'Brasil',
                'deadline': datetime.now() + timedelta(days=30),
                'amount': 'R$ 3.000/mês',
                'source': 'CNPq',
                'source_url': 'https://www.gov.br/cnpq/pt-br',
                'tags': ['Healthtech', 'Bolsa', 'P&D'],
                'collected_at': datetime.now()
            },
            {
                'external_id': 'eu_2024_003',
                'title': 'Horizonte Europa - Green Deal',
                'description': 'Funding para startups europeias focadas em soluções de sustentabilidade e energia limpa.',
                'category': 'Energia',
                'type': 'investimento',
                'region': 'Europa',
                'deadline': datetime.now() + timedelta(days=60),
                'amount': '€ 2.000.000',
                'source': 'União Europeia',
                'source_url': 'https://ec.europa.eu/info/horizon-europe_en',
                'tags': ['Sustentabilidade', 'Europa', 'Green Deal'],
                'collected_at': datetime.now()
            }
        ]
        
        return mock_data