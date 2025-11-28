# FundingAI - Sistema Inteligente de Oportunidades de Financiamento

## 🚀 Visão Geral

FundingAI é uma aplicação SaaS que utiliza inteligência artificial para buscar, classificar e recomendar oportunidades de financiamento para startups. O sistema emprega CrewAI para orquestrar múltiplos agentes especializados, LangChain para processamento de linguagem natural, e Pinecone como banco vetorial para busca semântica.

## 🏗️ Arquitetura

### Backend (Python)
- **FastAPI**: Framework web moderno e rápido
- **CrewAI**: Orquestração de agentes especializados
- **LangChain**: Pipeline de processamento de linguagem natural
- **Pinecone**: Banco vetorial para embeddings e busca semântica
- **PostgreSQL**: Banco de dados relacional
- **Redis**: Cache e filas de tarefas
- **Celery**: Processamento assíncrono de tarefas

### Frontend (React)
- **React + TypeScript**: Interface de usuário moderna
- **Tailwind CSS**: Estilização responsiva
- **Lucide React**: Ícones consistentes

## 🤖 Agentes Especializados

### 1. Agente de Coleta
- **Função**: Crawler que busca oportunidades em fontes pré-definidas
- **Fontes**: FINEP, CNPq, FAPESP, CAPES, União Europeia, aceleradoras
- **Tecnologias**: BeautifulSoup, Scrapy, requests

### 2. Agente de Classificação
- **Função**: Categoriza oportunidades por área e tipo
- **Categorias**: IA, Saúde, Energia, Fintech, Agtech, etc.
- **Tipos**: Editais, bolsas, investimentos

### 3. Agente de Ranqueamento
- **Função**: Ranqueia oportunidades usando RAG + embeddings
- **Critérios**: Perfil da startup, TRL, segmento, região
- **Tecnologia**: OpenAI embeddings + Pinecone

### 4. Agente de Notificação
- **Função**: Envia alertas personalizados
- **Canais**: Email (SendGrid), dashboard
- **Personalização**: Baseada no perfil e preferências

## 🔧 Configuração e Instalação

### Pré-requisitos
```bash
Python 3.8+
Node.js 16+
PostgreSQL
Redis
```

### Backend Setup
```bash
# Clone o repositório
git clone <repository-url>
cd funding-saas

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com suas credenciais

# Executar migrações
alembic upgrade head

# Iniciar servidor
python run.py
```

### Frontend Setup
```bash
# Instalar dependências
npm install

# Iniciar desenvolvimento
npm run dev
```

## 🔑 Variáveis de Ambiente

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/funding_saas

# Redis
REDIS_URL=redis://localhost:6379

# OpenAI
OPENAI_API_KEY=your_openai_api_key_here

# Pinecone
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=your_pinecone_environment
PINECONE_INDEX_NAME=funding-opportunities

# JWT
SECRET_KEY=your_secret_key_here

# Email
SENDGRID_API_KEY=your_sendgrid_api_key_here
FROM_EMAIL=noreply@fundingai.com
```

## 📊 Funcionalidades Principais

### 🔍 Busca Inteligente
- Consultas em linguagem natural
- RAG (Retrieval-Augmented Generation)
- Respostas contextualizadas
- Filtros avançados

### 📈 Dashboard Personalizado
- Oportunidades ranqueadas por relevância
- Estatísticas e métricas
- Filtros por categoria, região, tipo
- Exportação em CSV/PDF

### 🎯 Sistema de Alertas
- Notificações personalizadas
- Frequência configurável (diário, semanal, mensal)
- Filtros baseados no perfil da startup

### 👤 Perfil da Startup
- Informações detalhadas (segmento, TRL, área)
- Preferências de notificação
- Histórico de candidaturas

### 🤖 Monitoramento de Agentes
- Status em tempo real
- Logs de execução
- Métricas de performance
- Controle manual de pipelines

## 🔄 Fluxo de Dados

1. **Coleta**: Agentes coletam dados de fontes externas
2. **Classificação**: Oportunidades são categorizadas automaticamente
3. **Indexação**: Documentos são processados e indexados no Pinecone
4. **Ranqueamento**: Algoritmos de ML ranqueiam por relevância
5. **Notificação**: Usuários recebem alertas personalizados

## 🚀 Deploy

### Docker
```bash
# Build da aplicação
docker-compose build

# Iniciar serviços
docker-compose up -d
```

### Produção
- Configure variáveis de ambiente de produção
- Use PostgreSQL e Redis em produção
- Configure HTTPS
- Monitore logs e métricas

## 📝 API Endpoints

### Autenticação
- `POST /api/auth/register` - Registro de usuário
- `POST /api/auth/login` - Login

### Usuários
- `GET /api/users/me` - Perfil do usuário
- `PUT /api/users/me` - Atualizar perfil

### Oportunidades
- `GET /api/opportunities` - Listar oportunidades
- `GET /api/opportunities/{id}` - Detalhes da oportunidade
- `POST /api/opportunities/{id}/favorite` - Favoritar

### Busca
- `POST /api/search/semantic` - Busca semântica
- `GET /api/search/suggestions` - Sugestões de busca

### Agentes
- `GET /api/agents/status` - Status dos agentes
- `GET /api/agents/logs` - Logs de execução
- `POST /api/agents/run-collection` - Executar coleta manual

## 🧪 Testes

```bash
# Executar testes
pytest

# Testes com cobertura
pytest --cov=app

# Testes específicos
pytest tests/test_agents.py
```

## 📚 Documentação

- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Swagger UI**: Interface interativa da API

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para detalhes.

## 🆘 Suporte

Para suporte técnico ou dúvidas:
- Email: jrangel12@unifesp.br
- Issues: GitHub Issues
- Documentação: Wiki do projeto

---
