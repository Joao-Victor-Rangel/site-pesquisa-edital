from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import asyncio

from app.database import get_db
from app.models import User, Opportunity, UserFavorite
from app.schemas import Opportunity as OpportunitySchema
from app.core.security import get_current_user
from app.core.crew_manager import crew_manager

router = APIRouter()

@router.get("/", response_model=List[OpportunitySchema])
async def get_opportunities(
    category: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    limit: int = Query(20, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Get mock opportunities for demo
    mock_opportunities = [
        {
            'id': 1,
            'external_id': 'finep_2024_001',
            'title': 'FINEP - Subvenção Econômica para Startups de IA',
            'description': 'Programa de apoio financeiro para startups desenvolvedoras de soluções de inteligência artificial com foco em impacto social.',
            'category': 'Inteligência Artificial',
            'type': 'edital',
            'region': 'Brasil',
            'deadline': '2024-03-15T00:00:00',
            'amount': 'R$ 500.000',
            'source': 'FINEP',
            'source_url': 'https://www.finep.gov.br/chamadas-publicas',
            'relevance_score': 95.0,
            'tags': ['IA', 'Startup', 'Inovação', 'Subvenção'],
            'is_active': True,
            'created_at': '2024-01-15T10:00:00',
            'updated_at': '2024-01-15T10:00:00',
            'is_favorite': False
        },
        {
            'id': 2,
            'external_id': 'cnpq_2024_002',
            'title': 'CNPq - Bolsa de Desenvolvimento Tecnológico',
            'description': 'Bolsa para desenvolvimento de tecnologias disruptivas em healthtech com duração de 24 meses.',
            'category': 'Saúde',
            'type': 'bolsa',
            'region': 'Brasil',
            'deadline': '2024-02-28T00:00:00',
            'amount': 'R$ 3.000/mês',
            'source': 'CNPq',
            'source_url': 'https://www.gov.br/cnpq/pt-br',
            'relevance_score': 87.0,
            'tags': ['Healthtech', 'Bolsa', 'P&D'],
            'is_active': True,
            'created_at': '2024-01-14T15:00:00',
            'updated_at': '2024-01-14T15:00:00',
            'is_favorite': True
        },
        {
            'id': 3,
            'external_id': 'eu_2024_003',
            'title': 'Horizonte Europa - Green Deal',
            'description': 'Funding para startups europeias focadas em soluções de sustentabilidade e energia limpa.',
            'category': 'Energia',
            'type': 'investimento',
            'region': 'Europa',
            'deadline': '2024-04-10T00:00:00',
            'amount': '€ 2.000.000',
            'source': 'União Europeia',
            'source_url': 'https://ec.europa.eu/info/horizon-europe_en',
            'relevance_score': 78.0,
            'tags': ['Sustentabilidade', 'Europa', 'Green Deal'],
            'is_active': True,
            'created_at': '2024-01-13T09:00:00',
            'updated_at': '2024-01-13T09:00:00',
            'is_favorite': False
        }
    ]
    
    # Apply filters
    filtered_opportunities = mock_opportunities
    
    if category:
        filtered_opportunities = [opp for opp in filtered_opportunities if opp['category'] == category]
    
    if type:
        filtered_opportunities = [opp for opp in filtered_opportunities if opp['type'] == type]
    
    if region:
        filtered_opportunities = [opp for opp in filtered_opportunities if opp['region'] == region]
    
    # Rank opportunities based on user profile
    user_profile = {
        'startup_segment': current_user.startup_segment,
        'startup_trl': current_user.startup_trl,
        'startup_area': current_user.startup_area,
        'preferred_regions': current_user.preferred_regions or [],
        'preferred_categories': current_user.preferred_categories or [],
        'min_amount': current_user.min_amount
    }
    
    ranked_opportunities = await crew_manager.run_ranking_pipeline(
        filtered_opportunities, 
        user_profile
    )
    
    return ranked_opportunities[:limit]

@router.get("/{opportunity_id}", response_model=OpportunitySchema)
def get_opportunity(
    opportunity_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Mock single opportunity
    if opportunity_id == 1:
        return {
            'id': 1,
            'external_id': 'finep_2024_001',
            'title': 'FINEP - Subvenção Econômica para Startups de IA',
            'description': 'Programa de apoio financeiro para startups desenvolvedoras de soluções de inteligência artificial com foco em impacto social.',
            'category': 'Inteligência Artificial',
            'type': 'edital',
            'region': 'Brasil',
            'deadline': '2024-03-15T00:00:00',
            'amount': 'R$ 500.000',
            'source': 'FINEP',
            'source_url': 'https://www.finep.gov.br/chamadas-publicas',
            'relevance_score': 95.0,
            'tags': ['IA', 'Startup', 'Inovação', 'Subvenção'],
            'is_active': True,
            'created_at': '2024-01-15T10:00:00',
            'updated_at': '2024-01-15T10:00:00',
            'is_favorite': False
        }
    
    raise HTTPException(status_code=404, detail="Opportunity not found")

@router.post("/{opportunity_id}/favorite")
def toggle_favorite(
    opportunity_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Mock favorite toggle
    return {"message": "Favorite toggled successfully", "is_favorite": True}

@router.get("/export/csv")
def export_opportunities_csv(
    current_user: User = Depends(get_current_user)
):
    # Mock CSV export
    return {"message": "CSV export would be generated here", "download_url": "/downloads/opportunities.csv"}