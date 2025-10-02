import React, { useState, useEffect } from 'react';
import { Search, Bell, User, Filter, TrendingUp, MapPin, Calendar, DollarSign, FileText, Download, MessageCircle, Settings, LogOut, Eye, Heart, Users, Zap, Bot, Activity } from 'lucide-react';

// Types
interface Opportunity {
  id: string;
  title: string;
  description: string;
  category: string;
  type: 'edital' | 'bolsa' | 'investimento';
  region: string;
  deadline: string;
  amount: string;
  source: string;
  relevanceScore: number;
  tags: string[];
  isNew: boolean;
  isFavorite: boolean;
}

interface UserProfile {
  name: string;
  email: string;
  startup: {
    name: string;
    segment: string;
    trl: number;
    area: string;
    description: string;
  };
  preferences: {
    regions: string[];
    categories: string[];
    minAmount: string;
    alertFrequency: string;
  };
}

// Mock Data
const mockOpportunities: Opportunity[] = [
  {
    id: '1',
    title: 'FINEP - Subvenção Econômica para Startups de IA',
    description: 'Programa de apoio financeiro para startups desenvolvedoras de soluções de inteligência artificial com foco em impacto social.',
    category: 'Inteligência Artificial',
    type: 'edital',
    region: 'Brasil',
    deadline: '2024-03-15',
    amount: 'R$ 500.000',
    source: 'FINEP',
    relevanceScore: 95,
    tags: ['IA', 'Startup', 'Inovação', 'Subvenção'],
    isNew: true,
    isFavorite: false
  },
  {
    id: '2',
    title: 'CNPq - Bolsa de Desenvolvimento Tecnológico',
    description: 'Bolsa para desenvolvimento de tecnologias disruptivas em healthtech com duração de 24 meses.',
    category: 'Saúde',
    type: 'bolsa',
    region: 'Brasil',
    deadline: '2024-02-28',
    amount: 'R$ 3.000/mês',
    source: 'CNPq',
    relevanceScore: 87,
    tags: ['Healthtech', 'Bolsa', 'P&D'],
    isNew: false,
    isFavorite: true
  },
  {
    id: '3',
    title: 'Horizonte Europa - Green Deal',
    description: 'Funding para startups europeias focadas em soluções de sustentabilidade e energia limpa.',
    category: 'Energia',
    type: 'investimento',
    region: 'Europa',
    deadline: '2024-04-10',
    amount: '€ 2.000.000',
    source: 'União Europeia',
    relevanceScore: 78,
    tags: ['Sustentabilidade', 'Europa', 'Green Deal'],
    isNew: true,
    isFavorite: false
  }
];

const mockUser: UserProfile = {
  name: 'Ana Silva',
  email: 'ana@startup.com',
  startup: {
    name: 'TechHealth AI',
    segment: 'Healthtech',
    trl: 6,
    area: 'Inteligência Artificial aplicada à Saúde',
    description: 'Desenvolvemos soluções de IA para diagnóstico médico'
  },
  preferences: {
    regions: ['Brasil', 'América Latina'],
    categories: ['Saúde', 'Inteligência Artificial'],
    minAmount: '100000',
    alertFrequency: 'semanal'
  }
};

// Components
const Navbar = ({ user, currentView, setCurrentView, onLogout }: any) => (
<nav className="bg-white shadow-sm border-b border-gray-200">
  <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div className="flex justify-between items-center h-16">
      <div className="flex items-center space-x-8">
        
        <div className="flex items-center space-x-2">
          <img 
            src="src\assets\logo1.png"   
            alt="OportunidadeIA" 
            className="h-8 w-auto"
          />
          <span className="text-xl font-bold text-gray-900">OportunidadeIA</span>
        </div>

        <div className="flex space-x-6">
          {['dashboard', 'search', 'profile', 'agents'].map((view) => (
            <button
              key={view}
              onClick={() => setCurrentView(view)}
              className={`px-3 py-2 text-sm font-medium capitalize transition-colors ${
                currentView === view 
                  ? 'text-blue-600 border-b-2 border-blue-600' 
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              {view === 'agents' ? 'Agentes' : view === 'search' ? 'Busca' : view === 'profile' ? 'Perfil' : 'Dashboard'}
            </button>
          ))}
        </div>
      </div>
      
      <div className="flex items-center space-x-4">
        <button className="p-2 text-gray-400 hover:text-gray-600 transition-colors relative">
          <Bell className="h-5 w-5" />
          <span className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full"></span>
        </button>
        
        <div className="relative group">
          <button className="flex items-center space-x-2 p-2 rounded-lg hover:bg-gray-50 transition-colors">
            <div className="w-8 h-8 bg-gradient-to-br from-green-400 to-blue-500 rounded-full flex items-center justify-center">
              <User className="h-4 w-4 text-white" />
            </div>
            <span className="text-sm font-medium text-gray-700">{user?.name}</span>
          </button>
          
          <div className="absolute right-0 top-12 w-48 bg-white rounded-lg shadow-lg border border-gray-200 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none group-hover:pointer-events-auto">
            <button 
              onClick={onLogout}
              className="w-full flex items-center space-x-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors rounded-lg"
            >
              <LogOut className="h-4 w-4" />
              <span>Sair</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</nav>
);


const OpportunityCard = ({ opportunity, onToggleFavorite, onView }: any) => (
  <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-all duration-300 group">
    <div className="flex justify-between items-start mb-4">
      <div className="flex items-center space-x-3">
        <div className={`px-3 py-1 rounded-full text-xs font-medium ${
          opportunity.type === 'edital' ? 'bg-blue-100 text-blue-700' :
          opportunity.type === 'bolsa' ? 'bg-green-100 text-green-700' :
          'bg-purple-100 text-purple-700'
        }`}>
          {opportunity.type.charAt(0).toUpperCase() + opportunity.type.slice(1)}
        </div>
        {opportunity.isNew && (
          <div className="px-2 py-1 bg-red-100 text-red-700 rounded-full text-xs font-medium animate-pulse">
            Novo
          </div>
        )}
        <div className="flex items-center space-x-1 text-xs text-gray-500">
          <TrendingUp className="h-3 w-3" />
          <span>{opportunity.relevanceScore}% relevante</span>
        </div>
      </div>
      
      <button 
        onClick={() => onToggleFavorite(opportunity.id)}
        className="text-gray-400 hover:text-red-500 transition-colors"
      >
        <Heart className={`h-5 w-5 ${opportunity.isFavorite ? 'fill-red-500 text-red-500' : ''}`} />
      </button>
    </div>
    
    <h3 className="text-lg font-semibold text-gray-900 mb-2 group-hover:text-blue-600 transition-colors">
      {opportunity.title}
    </h3>
    
    <p className="text-gray-600 text-sm mb-4 line-clamp-2">
      {opportunity.description}
    </p>
    
    <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
      <div className="flex items-center space-x-4">
        <div className="flex items-center space-x-1">
          <MapPin className="h-4 w-4" />
          <span>{opportunity.region}</span>
        </div>
        <div className="flex items-center space-x-1">
          <Calendar className="h-4 w-4" />
          <span>{new Date(opportunity.deadline).toLocaleDateString('pt-BR')}</span>
        </div>
        <div className="flex items-center space-x-1">
          <DollarSign className="h-4 w-4" />
          <span>{opportunity.amount}</span>
        </div>
      </div>
    </div>
    
    <div className="flex flex-wrap gap-2 mb-4">
      {opportunity.tags.slice(0, 3).map((tag: string) => (
        <span key={tag} className="px-2 py-1 bg-gray-100 text-gray-600 rounded-lg text-xs">
          {tag}
        </span>
      ))}
      {opportunity.tags.length > 3 && (
        <span className="px-2 py-1 bg-gray-100 text-gray-600 rounded-lg text-xs">
          +{opportunity.tags.length - 3}
        </span>
      )}
    </div>
    
    <div className="flex justify-between items-center">
      <span className="text-xs text-gray-500">Fonte: {opportunity.source}</span>
      <button 
        onClick={() => onView(opportunity)}
        className="flex items-center space-x-1 px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
      >
        <Eye className="h-4 w-4" />
        <span>Ver detalhes</span>
      </button>
    </div>
  </div>
);

const Dashboard = ({ opportunities, onToggleFavorite, onView }: any) => {
  const [filter, setFilter] = useState({ category: 'all', type: 'all', region: 'all' });
  
  const filteredOpportunities = opportunities.filter((opp: Opportunity) => {
    return (filter.category === 'all' || opp.category === filter.category) &&
           (filter.type === 'all' || opp.type === filter.type) &&
           (filter.region === 'all' || opp.region === filter.region);
  });

  const stats = [
    { label: 'Oportunidades Ativas', value: opportunities.length, icon: FileText, color: 'blue' },
    { label: 'Novas Esta Semana', value: opportunities.filter((o: Opportunity) => o.isNew).length, icon: TrendingUp, color: 'green' },
    { label: 'Favoritas', value: opportunities.filter((o: Opportunity) => o.isFavorite).length, icon: Heart, color: 'red' },
    { label: 'Alta Relevância', value: opportunities.filter((o: Opportunity) => o.relevanceScore >= 90).length, icon: Zap, color: 'purple' }
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Dashboard</h1>
        <p className="text-gray-600">Acompanhe as melhores oportunidades para sua startup</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {stats.map((stat, index) => (
          <div key={index} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 mb-1">{stat.label}</p>
                <p className="text-3xl font-bold text-gray-900">{stat.value}</p>
              </div>
              <div className={`p-3 rounded-lg bg-${stat.color}-100`}>
                <stat.icon className={`h-6 w-6 text-${stat.color}-600`} />
              </div>
            </div>
          </div>
        ))}
      </div>
      
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-8">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-gray-900">Filtros</h2>
          <Filter className="h-5 w-5 text-gray-400" />
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Categoria</label>
            <select 
              value={filter.category}
              onChange={(e) => setFilter({...filter, category: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="all">Todas</option>
              <option value="Inteligência Artificial">IA</option>
              <option value="Saúde">Saúde</option>
              <option value="Energia">Energia</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Tipo</label>
            <select 
              value={filter.type}
              onChange={(e) => setFilter({...filter, type: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="all">Todos</option>
              <option value="edital">Editais</option>
              <option value="bolsa">Bolsas</option>
              <option value="investimento">Investimentos</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Região</label>
            <select 
              value={filter.region}
              onChange={(e) => setFilter({...filter, region: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="all">Todas</option>
              <option value="Brasil">Brasil</option>
              <option value="Europa">Europa</option>
              <option value="América Latina">América Latina</option>
            </select>
          </div>
        </div>
      </div>
      
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-gray-900">
          Oportunidades ({filteredOpportunities.length})
        </h2>
        <button className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors">
          <Download className="h-4 w-4" />
          <span>Exportar</span>
        </button>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {filteredOpportunities.map((opportunity: Opportunity) => (
          <OpportunityCard 
            key={opportunity.id} 
            opportunity={opportunity} 
            onToggleFavorite={onToggleFavorite}
            onView={onView}
          />
        ))}
      </div>
    </div>
  );
};

const SmartSearch = () => {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Olá! Sou seu assistente de busca inteligente. Posso te ajudar a encontrar oportunidades de financiamento. Pergunte algo como "Quais bolsas de IA estão abertas no Brasil?" ou "Editais de healthtech com prazo até março".' }
  ]);
  
  const handleSend = () => {
    if (!query.trim()) return;
    
    const userMessage = { role: 'user', content: query };
    setMessages(prev => [...prev, userMessage]);
    
    // Simulação de resposta inteligente
    setTimeout(() => {
      const response = { 
        role: 'assistant', 
        content: `Com base na sua consulta "${query}", encontrei 3 oportunidades relevantes:\n\n1. **FINEP - Subvenção IA** - R$ 500.000 - Prazo: 15/03/2024\n2. **CNPq - Bolsa Healthtech** - R$ 3.000/mês - Prazo: 28/02/2024\n3. **Horizonte Europa** - € 2.000.000 - Prazo: 10/04/2024\n\nGostaria de ver mais detalhes de alguma dessas oportunidades?`
      };
      setMessages(prev => [...prev, response]);
    }, 1000);
    
    setQuery('');
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Busca Inteligente</h1>
        <p className="text-gray-600">Use inteligência artificial para encontrar as melhores oportunidades</p>
      </div>
      
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 h-96 flex flex-col">
        <div className="flex items-center space-x-3 p-4 border-b border-gray-200">
          <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-blue-600 rounded-full flex items-center justify-center">
            <Bot className="h-4 w-4 text-white" />
          </div>
          <span className="font-medium text-gray-900">Assistente AI</span>
          <div className="flex items-center space-x-1">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span className="text-sm text-green-600">Online</span>
          </div>
        </div>
        
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((message, index) => (
            <div key={index} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                message.role === 'user' 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-gray-100 text-gray-900'
              }`}>
                <p className="text-sm whitespace-pre-line">{message.content}</p>
              </div>
            </div>
          ))}
        </div>
        
        <div className="p-4 border-t border-gray-200">
          <div className="flex space-x-2">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Digite sua pergunta sobre oportunidades..."
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <button 
              onClick={handleSend}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <MessageCircle className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

const Profile = ({ user, onUpdateProfile }: any) => {
  const [editMode, setEditMode] = useState(false);
  const [formData, setFormData] = useState(user);
  
  const handleSave = () => {
    onUpdateProfile(formData);
    setEditMode(false);
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Perfil da Startup</h1>
        <p className="text-gray-600">Mantenha seus dados atualizados para receber melhores recomendações</p>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-gray-900">Informações da Startup</h2>
              <button 
                onClick={() => editMode ? handleSave() : setEditMode(true)}
                className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <Settings className="h-4 w-4" />
                <span>{editMode ? 'Salvar' : 'Editar'}</span>
              </button>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Nome da Startup</label>
                <input
                  type="text"
                  value={formData.startup.name}
                  onChange={(e) => setFormData({...formData, startup: {...formData.startup, name: e.target.value}})}
                  disabled={!editMode}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-50"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Segmento</label>
                <input
                  type="text"
                  value={formData.startup.segment}
                  onChange={(e) => setFormData({...formData, startup: {...formData.startup, segment: e.target.value}})}
                  disabled={!editMode}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-50"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Nível TRL</label>
                <select
                  value={formData.startup.trl}
                  onChange={(e) => setFormData({...formData, startup: {...formData.startup, trl: parseInt(e.target.value)}})}
                  disabled={!editMode}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-50"
                >
                  {[1,2,3,4,5,6,7,8,9].map(level => (
                    <option key={level} value={level}>TRL {level}</option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Área de Atuação</label>
                <input
                  type="text"
                  value={formData.startup.area}
                  onChange={(e) => setFormData({...formData, startup: {...formData.startup, area: e.target.value}})}
                  disabled={!editMode}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-50"
                />
              </div>
            </div>
            
            <div className="mt-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">Descrição</label>
              <textarea
                value={formData.startup.description}
                onChange={(e) => setFormData({...formData, startup: {...formData.startup, description: e.target.value}})}
                disabled={!editMode}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-50"
              />
            </div>
          </div>
        </div>
        
        <div>
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-6">Preferências de Alerta</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Frequência</label>
                <select
                  value={formData.preferences.alertFrequency}
                  onChange={(e) => setFormData({...formData, preferences: {...formData.preferences, alertFrequency: e.target.value}})}
                  disabled={!editMode}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-50"
                >
                  <option value="diario">Diário</option>
                  <option value="semanal">Semanal</option>
                  <option value="mensal">Mensal</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Valor Mínimo</label>
                <input
                  type="text"
                  value={formData.preferences.minAmount}
                  onChange={(e) => setFormData({...formData, preferences: {...formData.preferences, minAmount: e.target.value}})}
                  disabled={!editMode}
                  placeholder="Ex: 50000"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-50"
                />
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mt-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Estatísticas</h3>
            
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Oportunidades vistas</span>
                <span className="font-semibold">47</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Candidaturas</span>
                <span className="font-semibold">12</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Taxa de sucesso</span>
                <span className="font-semibold">25%</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const AgentMonitoring = () => {
  const agents = [
    { name: 'Agente de Coleta', status: 'active', lastRun: '2024-01-15 10:30', collected: 127, success: 95 },
    { name: 'Agente de Classificação', status: 'active', lastRun: '2024-01-15 10:45', processed: 89, success: 98 },
    { name: 'Agente de Ranqueamento', status: 'idle', lastRun: '2024-01-15 09:15', ranked: 67, success: 91 },
    { name: 'Agente de Notificação', status: 'active', lastRun: '2024-01-15 11:00', sent: 23, success: 100 }
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Monitoramento de Agentes</h1>
        <p className="text-gray-600">Acompanhe a performance dos agentes de IA em tempo real</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {agents.map((agent, index) => (
          <div key={index} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-gray-900">{agent.name}</h3>
              <div className={`w-3 h-3 rounded-full ${
                agent.status === 'active' ? 'bg-green-500 animate-pulse' : 
                agent.status === 'idle' ? 'bg-yellow-500' : 'bg-red-500'
              }`}></div>
            </div>
            
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Última execução:</span>
                <span className="font-medium">{agent.lastRun}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Processados:</span>
                <span className="font-medium">{agent.collected || agent.processed || agent.ranked || agent.sent}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Taxa de sucesso:</span>
                <span className="font-medium text-green-600">{agent.success}%</span>
              </div>
            </div>
            
            <div className="mt-4">
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-gradient-to-r from-green-400 to-green-600 h-2 rounded-full transition-all duration-300"
                  style={{width: `${agent.success}%`}}
                ></div>
              </div>
            </div>
          </div>
        ))}
      </div>
      
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-gray-900">Log de Atividades</h2>
          <Activity className="h-5 w-5 text-gray-400" />
        </div>
        
        <div className="space-y-4">
          {[
            { time: '11:00', agent: 'Notificação', action: 'Enviou 23 alertas por email', status: 'success' },
            { time: '10:45', agent: 'Classificação', action: 'Classificou 89 oportunidades', status: 'success' },
            { time: '10:30', agent: 'Coleta', action: 'Coletou 127 novos editais', status: 'success' },
            { time: '09:15', agent: 'Ranqueamento', action: 'Processou ranqueamento de 67 oportunidades', status: 'success' },
            { time: '08:00', agent: 'Coleta', action: 'Iniciou varredura em sites governamentais', status: 'info' }
          ].map((log, index) => (
            <div key={index} className="flex items-center space-x-4 py-3 border-b border-gray-100 last:border-b-0">
              <div className="text-sm text-gray-500 min-w-[4rem]">{log.time}</div>
              <div className={`w-3 h-3 rounded-full ${
                log.status === 'success' ? 'bg-green-500' : 
                log.status === 'error' ? 'bg-red-500' : 'bg-blue-500'
              }`}></div>
              <div className="flex-1">
                <span className="font-medium text-gray-900">{log.agent}:</span>
                <span className="text-gray-600 ml-2">{log.action}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

const LoginForm = ({ onLogin }: any) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isSignUp, setIsSignUp] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onLogin();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center px-4">
  <div className="max-w-md w-full">
    <div className="text-center mb-8">
      {/* Logo */}
      <div className="flex justify-center mb-4">
        <img 
          src="src\assets\logo.png"   
          alt="OportunidadeIA" 
          className="h-16 w-auto"
        />
      </div>

      <h1 className="text-3xl font-bold text-gray-900 mb-2">OportunidadeIA</h1>
      <p className="text-gray-600">Encontre as melhores oportunidades para sua startup</p>
    </div>
    
    <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-8">
      <div className="mb-6">
        <h2 className="text-2xl font-semibold text-gray-900 mb-2">
          {isSignUp ? 'Criar conta' : 'Entrar'}
        </h2>
        <p className="text-gray-600">
          {isSignUp ? 'Cadastre sua startup e comece a receber oportunidades' : 'Acesse sua conta'}
        </p>
      </div>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="seu@email.com"
            required
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Senha</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="••••••••"
            required
          />
        </div>
        
        <button
          type="submit"
          className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-2 rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all duration-200 font-medium"
        >
          {isSignUp ? 'Criar conta' : 'Entrar'}
        </button>
      </form>
      
      <div className="mt-6 text-center">
        <button
          onClick={() => setIsSignUp(!isSignUp)}
          className="text-blue-600 hover:text-blue-700 text-sm font-medium"
        >
          {isSignUp ? 'Já tem conta? Faça login' : 'Não tem conta? Cadastre-se'}
        </button>
      </div>
    </div>
  </div>
</div>

  );
};

// Main App Component
function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [currentView, setCurrentView] = useState('dashboard');
  const [user, setUser] = useState(mockUser);
  const [opportunities, setOpportunities] = useState(mockOpportunities);

  const handleLogin = () => {
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    setCurrentView('dashboard');
  };

  const handleToggleFavorite = (id: string) => {
    setOpportunities(opportunities.map(opp => 
      opp.id === id ? {...opp, isFavorite: !opp.isFavorite} : opp
    ));
  };

  const handleViewOpportunity = (opportunity: Opportunity) => {
    alert(`Visualizando: ${opportunity.title}\n\nEm uma versão completa, esta seria uma página detalhada com informações completas do edital, requisitos, documentos necessários, cronograma, etc.`);
  };

  const handleUpdateProfile = (newProfile: UserProfile) => {
    setUser(newProfile);
  };

  if (!isAuthenticated) {
    return <LoginForm onLogin={handleLogin} />;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar 
        user={user}
        currentView={currentView}
        setCurrentView={setCurrentView}
        onLogout={handleLogout}
      />
      
      {currentView === 'dashboard' && (
        <Dashboard 
          opportunities={opportunities}
          onToggleFavorite={handleToggleFavorite}
          onView={handleViewOpportunity}
        />
      )}
      
      {currentView === 'search' && <SmartSearch />}
      
      {currentView === 'profile' && (
        <Profile 
          user={user}
          onUpdateProfile={handleUpdateProfile}
        />
      )}
      
      {currentView === 'agents' && <AgentMonitoring />}
    </div>
  );
}

export default App;