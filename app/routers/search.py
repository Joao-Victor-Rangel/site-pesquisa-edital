from fastapi import APIRouter, Depends, HTTPException
from typing import Optional, Dict, Any

from app.models import User
from app.schemas import SearchQuery, SearchResponse
from app.core.security import get_current_user
from app.core.crew_manager import crew_manager

router = APIRouter()

@router.post("/semantic", response_model=SearchResponse)
async def semantic_search(
    search_query: SearchQuery,
    current_user: User = Depends(get_current_user)
):
    """Perform semantic search using RAG"""
    try:
        result = await crew_manager.semantic_search(
            query=search_query.query,
            filters=search_query.filters,
            top_k=search_query.limit
        )
        
        return SearchResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/suggestions")
def get_search_suggestions(
    q: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Get search suggestions based on user profile and query"""
    
    # Mock suggestions based on user profile
    suggestions = []
    
    if current_user.startup_segment:
        suggestions.append(f"Editais de {current_user.startup_segment}")
        suggestions.append(f"Bolsas para {current_user.startup_segment}")
    
    if current_user.preferred_regions:
        for region in current_user.preferred_regions[:2]:
            suggestions.append(f"Oportunidades em {region}")
    
    # General suggestions
    suggestions.extend([
        "Editais FINEP abertos",
        "Bolsas CNPq para startups",
        "Investimentos em IA",
        "Financiamento para healthtech",
        "Oportunidades Horizonte Europa",
        "Subvenção econômica 2024"
    ])
    
    # Filter by query if provided
    if q:
        suggestions = [s for s in suggestions if q.lower() in s.lower()]
    
    return {"suggestions": suggestions[:10]}

@router.get("/categories")
def get_search_categories(current_user: User = Depends(get_current_user)):
    """Get available search categories"""
    return {
        "categories": [
            "Inteligência Artificial",
            "Saúde",
            "Energia",
            "Fintech",
            "Agtech",
            "Educação",
            "Mobilidade",
            "Indústria 4.0"
        ],
        "types": [
            "edital",
            "bolsa",
            "investimento"
        ],
        "regions": [
            "Brasil",
            "América Latina",
            "Europa",
            "América do Norte",
            "Ásia"
        ]
    }