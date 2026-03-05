# 🎓 Plataforma Educativa com IA

Sistema inteligente de geração de conteúdo educacional personalizado usando GPT-4o-mini via OpenRouter e técnicas avançadas de Engenharia de Prompts.

## 🚀 Início Rápido

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Configurar API Key
cp .env.example .env
nano .env  # Adicione sua chave do OpenRouter

# 3. Executar
python app.py

# 4. Acessar
http://localhost:5000
```

## ✨ Características

- ✅ **Banco de Dados SQL Real**: SQLite + SQLAlchemy (sem mocks!)
- ✅ **Prompts Externalizados**: Todos em `prompts/*.txt` (editáveis sem tocar no código)
- ✅ **Configuração Completa via .env**: Temperature, max_tokens, penalties, etc.
- ✅ **4 Tipos de Conteúdo**: Explicações, exemplos, questões e mapas mentais
- ✅ **Cache Inteligente**: Economiza tokens e acelera respostas
- ✅ **Interface Web Moderna**: CRUD completo de estudantes
- ✅ **Código Produção**: Type hints, logging, validação robusta

## 🎛️ Configuração do Modelo (.env)

```env
# Model Configuration
MODEL_NAME=openai/gpt-4o-mini
MODEL_TEMPERATURE=0.7           # 0.0-2.0 (criatividade)
MODEL_MAX_TOKENS=2000           # Tamanho da resposta
MODEL_TOP_P=1.0                 # Nucleus sampling
MODEL_FREQUENCY_PENALTY=0.0     # Reduz repetições
MODEL_PRESENCE_PENALTY=0.0      # Muda de tópico
```

📖 **Guia completo**: `MODEL_CONFIG_GUIDE.md`

## 📁 Estrutura

```
V-LAB-2-Fase/
├── app.py                    # Flask + rotas API
├── models.py                 # SQLAlchemy models
├── prompt_engine.py          # Carrega templates externos
├── llm_service.py            # OpenRouter + cache
├── prompts/                  # 🌟 TODOS OS PROMPTS AQUI!
│   ├── system_*.txt         # Personas
│   ├── user_*.txt           # Instruções
│   └── template_*.txt       # Contextos
├── templates/index.html      # Interface web
├── educativa.db              # SQLite (auto-criado)
└── .env                      # Configurações
```

## 🎯 Como Usar

### 1. Cadastrar Estudante
- Aba **"👥 Gerenciar Estudantes"**
- Preencha: nome, idade, nível, estilo, interesses

### 2. Gerar Material
- Aba **"📚 Gerar Material"**
- Selecione estudante
- Digite tópico (ex: "Fotossíntese")
- Clique em gerar

### 3. Personalizar Prompts
```bash
# Edite os templates
nano prompts/system_conceptual_explanation.txt

# Reinicie ou limpe cache
curl -X POST http://localhost:5000/api/cache/clear
```

## 🔧 APIs Disponíveis

```bash
# Configuração do modelo
GET /api/config

# CRUD Estudantes
GET    /api/students
POST   /api/students
GET    /api/students/<id>
PUT    /api/students/<id>
DELETE /api/students/<id>

# Gerar conteúdo
POST /api/generate

# Histórico
GET /api/history
GET /api/history/<id>

# Cache
GET  /api/cache/stats
POST /api/cache/clear
```

## 🧠 Técnicas de Prompt Engineering

1. **Persona Prompting**: Cada tipo tem sua persona especializada
2. **Context Setting**: Perfil do estudante injetado
3. **Output Formatting**: JSON estruturado obrigatório
4. **Chain-of-Thought**: Raciocínio pedagógico explícito
5. **Template-based**: Prompts em arquivos separados

📖 **Detalhes**: `PROMPT_ENGINEERING_NOTES.md`

## 🎨 Editando Prompts

Todos os prompts estão em `prompts/` com nomenclatura padronizada:

- `system_*.txt`: Define persona + formato JSON
- `user_*.txt`: Instruções + variáveis `{topic}`, `{idade}`, etc.
- `template_*.txt`: Templates reutilizáveis

**Variáveis disponíveis:**
- `{nome}`, `{idade}`, `{nivel}`, `{estilo_aprendizagem}`
- `{interesses}`, `{descricao}`, `{topic}`
- `{student_context}` (contexto completo)

## 📊 Banco de Dados

### Tabela `students`
- Nome, idade, nível, estilo de aprendizagem
- Interesses (JSON array)
- Timestamps automáticos

### Tabela `generation_history`
- Relacionamento com estudante
- Tópico, tipo de prompt, versão
- Conteúdo gerado (JSON)
- Tokens usados, cache hit
- Timestamps

## 🐛 Troubleshooting

### API Key não configurada
```bash
cp .env.example .env
nano .env  # Adicione sua chave
```

### Banco corrompido
```bash
rm educativa.db
python app.py  # Recria automaticamente
```

### Prompts não carregam
```bash
# Verifique se o diretório existe
ls prompts/

# Teste imports
python -c "from prompt_engine import PromptEngine; pe = PromptEngine(); print('OK')"
```

## 📚 Documentação Completa

- `MODEL_CONFIG_GUIDE.md`: Guia de parâmetros do modelo
- `PROMPT_ENGINEERING_NOTES.md`: Técnicas avançadas
- `prompts/README.md`: Documentação dos templates

## 🎓 Requisitos

- Python 3.9+
- Conta OpenRouter (gratuita)
- Navegador moderno

## 📦 Dependências

```txt
flask==3.0.0
openai==1.12.0
python-dotenv==1.0.0
sqlalchemy==2.0.25
flask-sqlalchemy==3.1.1
```
## 👨‍💻 Desenvolvimento

```bash
# Ativar modo debug
export FLASK_DEBUG=True
export LOG_LEVEL=DEBUG

# Verificar ambiente
python check_environment.py

# Rodar testes
# (adicionar pytest conforme necessário)
```

---

**Desenvolvido como projeto educacional de Engenharia de Prompts e Full-Stack Python** 🎉
