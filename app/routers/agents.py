from fastapi import APIRouter, Depends
from typing import List
from datetime import datetime

from app.models import User
from app.schemas import AgentStatus, AgentLogEntry
from app.core.security import get_current_user
from app.core.crew_manager import crew_manager

router = APIRouter()

@router.get("/status", response_model=List[AgentStatus])
def get_agents_status(current_user: User = Depends(get_current_user)):
    """Get status of all agents"""
    return crew_manager.get_agent_status()

@router.get("/logs", response_model=List[AgentLogEntry])
def get_agent_logs(
    limit: int = 50,
    current_user: User = Depends(get_current_user)
):
    """Get recent agent logs"""
    # Mock logs for demo
    mock_logs = [
        {
            'id': 1,
            'agent_name': 'Agente de Notificação',
            'action': 'Enviou 23 alertas por email',
            'status': 'success',
            'details': {'emails_sent': 23, 'success_rate': 100},
            'execution_time': 2.5,
            'created_at': datetime.now()
        },
        {
            'id': 2,
            'agent_name': 'Agente de Classificação',
            'action': 'Classificou 89 oportunidades',
            'status': 'success',
            'details': {'opportunities_processed': 89, 'categories_assigned': 12},
            'execution_time': 15.3,
            'created_at': datetime.now()
        },
        {
            'id': 3,
            'agent_name': 'Agente de Coleta',
            'action': 'Coletou 127 novos editais',
            'status': 'success',
            'details': {'sources_scraped': 8, 'new_opportunities': 127},
            'execution_time': 45.7,
            'created_at': datetime.now()
        },
        {
            'id': 4,
            'agent_name': 'Agente de Ranqueamento',
            'action': 'Processou ranqueamento de 67 oportunidades',
            'status': 'success',
            'details': {'opportunities_ranked': 67, 'avg_score': 72.5},
            'execution_time': 8.2,
            'created_at': datetime.now()
        },
        {
            'id': 5,
            'agent_name': 'Agente de Coleta',
            'action': 'Iniciou varredura em sites governamentais',
            'status': 'running',
            'details': {'sources_in_progress': 3},
            'execution_time': None,
            'created_at': datetime.now()
        }
    ]
    
    return mock_logs[:limit]

@router.post("/run-collection")
async def trigger_collection(current_user: User = Depends(get_current_user)):
    """Manually trigger the collection pipeline"""
    result = await crew_manager.run_collection_pipeline()
    return {
        "message": "Collection pipeline triggered successfully",
        "result": result
    }

@router.post("/run-notifications")
async def trigger_notifications(current_user: User = Depends(get_current_user)):
    """Manually trigger notifications"""
    # Mock user list for demo
    users = [
        {
            'name': current_user.name,
            'email': current_user.email,
            'startup_name': current_user.startup_name,
            'alert_frequency': current_user.alert_frequency,
            'preferred_categories': current_user.preferred_categories or [],
            'preferred_regions': current_user.preferred_regions or []
        }
    ]
    
    # Mock opportunities
    opportunities = [
        {
            'id': 1,
            'title': 'FINEP - Subvenção Econômica para Startups de IA',
            'category': 'Inteligência Artificial',
            'region': 'Brasil',
            'relevance_score': 95.0
        }
    ]
    
    result = await crew_manager.run_notification_pipeline(users, opportunities)
    return {
        "message": "Notification pipeline triggered successfully",
        "result": result
    }