from crewai import Agent
from crewai.tools import BaseTool
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
import logging
from datetime import datetime, timedelta
import re

logger = logging.getLogger(__name__)

# ---------- TOOLS ----------

class WebScraperTool(BaseTool):
    name: str = "web_scraper"
    description: str = "Extrai informações de páginas web e retorna texto limpo"

    def _run(self, url: str) -> str:
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Remove script e style
            for script in soup(["script", "style"]):
                script.decompose()

            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)

            return text[:5000]  # limita tamanho
        except Exception as e:
            logger.error(f"Failed to scrape {url}: {e}")
            return f"Erro ao acessar {url}: {str(e)}"


class ContentParserTool(BaseTool):
    name: str = "content_parser"
    description: str = "Analisa e extrai dados estruturados de conteúdo HTML/texto"

    def _run(self, content: str) -> str:
        try:
            opportunities = []
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


# ---------- AGENTE PRINCIPAL ----------

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
            tools=[WebScraperTool(), ContentParserTool()]  # agora só BaseTool
        )

    def collect_opportunities(self) -> List[Dict[str, Any]]:
        try:
            url = "https://api.exemplo.com/oportunidades"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                opportunities = [
                    {
                        "id": item["id"],
                        "title": item.get("title", ""),
                        "category": item.get("category", ""),
                        "type": item.get("type", ""),
                        "region": item.get("region", ""),
                        "amount": item.get("amount", ""),
                        "source": "API Exemplo"
                    }
                    for item in data.get("results", [])
                ]
                return opportunities
            else:
                logger.error(f"Erro ao coletar oportunidades: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Falha na coleta de oportunidades: {e}")
            return []

    def get_mock_opportunities(self) -> List[Dict[str, Any]]:
        return [
            {
                'external_id': 'finep_2024_001',
                'title': 'FINEP - Subvenção Econômica para Startups de IA',
                'description': 'Programa de apoio financeiro para startups desenvolvedoras de soluções de IA.',
                'category': 'Inteligência Artificial',
                'type': 'edital',
                'region': 'Brasil',
                'deadline': datetime.now() + timedelta(days=45),
                'amount': 'R$ 500.000',
                'source': 'FINEP',
                'source_url': self.sources["finep"],
                'tags': ['IA', 'Startup', 'Inovação', 'Subvenção'],
                'collected_at': datetime.now()
            },
            {
                'external_id': 'cnpq_2024_002',
                'title': 'CNPq - Bolsa de Desenvolvimento Tecnológico',
                'description': 'Bolsa para desenvolvimento de tecnologias disruptivas em healthtech.',
                'category': 'Saúde',
                'type': 'bolsa',
                'region': 'Brasil',
                'deadline': datetime.now() + timedelta(days=30),
                'amount': 'R$ 3.000/mês',
                'source': 'CNPq',
                'source_url': self.sources["cnpq"],
                'tags': ['Healthtech', 'Bolsa', 'P&D'],
                'collected_at': datetime.now()
            }
        ]
