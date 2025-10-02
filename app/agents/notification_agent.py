from crewai import Agent, Task, Crew
from crewai.tools import BaseTool
from typing import List, Dict, Any
import logging
from datetime import datetime
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

logger = logging.getLogger(__name__)

# ---------- TOOLS ----------

class EmailSenderTool(BaseTool):
    name: str = "email_sender"
    description: str = "Envia emails personalizados usando SendGrid"

    def _run(self, email_data: str) -> str:
        try:
            sendgrid_api_key = os.getenv("SENDGRID_API_KEY")
            from_email = os.getenv("FROM_EMAIL", "noreply@fundingai.com")

            if not sendgrid_api_key:
                logger.warning("SendGrid API key not configurada")
                return "Email não enviado - configuração pendente"

            # Parse simples de dados do email
            lines = email_data.split('\n')
            email_info = {}
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    email_info[key.strip().lower()] = value.strip()

            to_email = email_info.get('para', '')
            subject = email_info.get('assunto', 'Nova oportunidade disponível')
            content = email_info.get('conteúdo', '')

            if not to_email or not content:
                return "Dados de email incompletos"

            message = Mail(
                from_email=from_email,
                to_emails=to_email,
                subject=subject,
                html_content=content
            )

            sg = SendGridAPIClient(api_key=sendgrid_api_key)
            sg.send(message)

            logger.info(f"Email enviado com sucesso para {to_email}")
            return f"Email enviado com sucesso para {to_email}"
        except Exception as e:
            logger.error(f"Erro ao enviar email: {e}")
            return f"Erro ao enviar email: {str(e)}"


class MessageGeneratorTool(BaseTool):
    name: str = "message_generator"
    description: str = "Gera mensagens personalizadas em HTML para notificações"

    def _run(self, message_data: str) -> str:
        try:
            # Parse simples de dados
            lines = message_data.split('\n')
            data = {}
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    data[key.strip().lower()] = value.strip()

            user_name = data.get('nome', 'Usuário')
            startup_name = data.get('startup', '')
            opportunities_count = data.get('oportunidades', '0')

            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                color: white; padding: 30px; border-radius: 10px; text-align: center;">
                        <h1 style="margin: 0; font-size: 28px;">🚀 FundingAI</h1>
                        <p style="margin: 10px 0 0 0; font-size: 16px;">
                            Novas oportunidades para {startup_name or 'sua startup'}
                        </p>
                    </div>
                    <div style="padding: 30px 0;">
                        <h2 style="color: #667eea;">Olá, {user_name}!</h2>
                        <p>Encontramos <strong>{opportunities_count} novas oportunidades</strong> 
                        que podem ser perfeitas para {startup_name or 'sua startup'}.</p>
                        <div style="background: #f8f9ff; padding: 20px; border-radius: 8px; margin: 20px 0;">
                            <h3 style="color: #667eea; margin-top: 0;">📊 Resumo das Oportunidades</h3>
                            <ul style="margin: 0; padding-left: 20px;">
                                <li>Editais governamentais com alta compatibilidade</li>
                                <li>Bolsas de desenvolvimento tecnológico</li>
                                <li>Oportunidades de investimento privado</li>
                            </ul>
                        </div>
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="https://fundingai.com/dashboard" 
                               style="background: #667eea; color: white; padding: 15px 30px; 
                                      text-decoration: none; border-radius: 5px; font-weight: bold;">
                                Ver Oportunidades
                            </a>
                        </div>
                        <p style="color: #666; font-size: 14px;">
                            💡 <strong>Dica:</strong> Acesse seu dashboard para ver análises detalhadas 
                            e scores de compatibilidade para cada oportunidade.
                        </p>
                    </div>
                    <div style="border-top: 1px solid #eee; padding-top: 20px; 
                                text-align: center; color: #666; font-size: 12px;">
                        <p>Este email foi enviado pelo FundingAI - Sistema Inteligente de Oportunidades</p>
                        <p>Para alterar suas preferências de notificação, 
                           <a href="https://fundingai.com/profile">clique aqui</a></p>
                    </div>
                </div>
            </body>
            </html>
            """
            return html_content
        except Exception as e:
            logger.error(f"Erro ao gerar mensagem: {e}")
            return "Erro ao gerar mensagem personalizada"


# ---------- AGENTE PRINCIPAL ----------

class NotificationAgent:
    def __init__(self):
        self.agent = Agent(
            role='Especialista em Notificações',
            goal='Enviar alertas personalizados sobre novas oportunidades',
            backstory="""Você é responsável por manter os usuários informados sobre 
            oportunidades relevantes. Você cria mensagens personalizadas e envia 
            notificações por email e dashboard de forma inteligente.""",
            verbose=True,
            allow_delegation=False,
            tools=[EmailSenderTool(), MessageGeneratorTool()]  # agora só BaseTool
        )

    def send_opportunity_alerts(
        self,
        users: List[Dict[str, Any]],
        opportunities: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        logger.info(f"Enviando alertas para {len(users)} usuários sobre {len(opportunities)} oportunidades")

        results = {'sent': 0, 'failed': 0, 'details': []}

        for user in users:
            try:
                user_opportunities = self._filter_opportunities_for_user(user, opportunities)
                if not user_opportunities:
                    continue

                notification_data = f"""
                Nome: {user.get('name', '')}
                Email: {user.get('email', '')}
                Startup: {user.get('startup_name', '')}
                Oportunidades: {len(user_opportunities)}
                Frequência: {user.get('alert_frequency', 'weekly')}
                """

                task = Task(
                    description=f"""
                    Crie e envie uma notificação personalizada para o usuário:
                    
                    {notification_data}
                    
                    A notificação deve:
                    1. Ser personalizada com o nome do usuário e startup
                    2. Destacar o número de novas oportunidades
                    3. Incluir um resumo das categorias encontradas
                    4. Ter um call-to-action claro para acessar o dashboard
                    5. Ser visualmente atrativa em HTML
                    """,
                    agent=self.agent
                )

                crew = Crew(agents=[self.agent], tasks=[task], verbose=False)
                result = crew.kickoff()

                results['sent'] += 1
                results['details'].append({
                    'user': user.get('email'),
                    'opportunities': len(user_opportunities),
                    'status': 'sent',
                    'result': str(result)
                })

            except Exception as e:
                logger.error(f"Erro ao enviar alerta para {user.get('email', '')}: {e}")
                results['failed'] += 1
                results['details'].append({
                    'user': user.get('email'),
                    'status': 'failed',
                    'error': str(e)
                })

        logger.info(f"Envio de alertas concluído: {results['sent']} enviados, {results['failed']} falharam")
        return results

    def _filter_opportunities_for_user(
        self,
        user: Dict[str, Any],
        opportunities: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        filtered = []
        user_categories = user.get('preferred_categories', [])
        user_regions = user.get('preferred_regions', [])
        min_amount = user.get('min_amount', '0')

        for opp in opportunities:
            if user_categories and opp.get('category') not in user_categories:
                continue
            if user_regions and opp.get('region') not in user_regions:
                continue
            if opp.get('relevance_score', 0) < 60:
                continue
            filtered.append(opp)

        return filtered

    def create_dashboard_notifications(
        self,
        user_id: int,
        opportunities: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        notifications = []
        for opp in opportunities:
            notifications.append({
                'user_id': user_id,
                'opportunity_id': opp.get('id'),
                'type': 'dashboard',
                'title': f"Nova oportunidade: {opp.get('title', '')}",
                'message': f"Encontramos uma oportunidade com {opp.get('relevance_score', 0):.0f}% de compatibilidade",
                'created_at': datetime.now(),
                'is_read': False
            })
        return notifications
