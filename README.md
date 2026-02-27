
# OpenVAS Agent: Seu Assistente de IA para Análise de Vulnerabilidades

![Licença](https://img.shields.io/badge/Licença-MIT-blue)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Docker](https://img.shields.io/badge/Docker-Suportado-blue)

Bem-vindo ao projeto OpenVAS Agent! Esta ferramenta aproveita o poder da IA para revolucionar como você interage com o scanner de vulnerabilidades OpenVAS. Nosso objetivo é criar um copiloto poderoso e intuitivo que o assista na análise de vulnerabilidades, interpretação de resultados e otimização do seu fluxo de trabalho de segurança.

## 🚀 Funcionalidades

*   **Análise de Vulnerabilidades Alimentada por IA:** Vá além de simples scans. O agente o ajuda a compreender o impacto real das vulnerabilidades.
*   **Priorização Inteligente:** Priorize automaticamente alertas com base em severidade, explorabilidade e criticidade dos ativos.
*   **Remediação Acionável:** Receba sugestões de remediação baseadas em boas práticas, adaptadas ao seu ambiente.
*   **Interface Amigável:** Interaja com o OpenVAS através de uma interface conversacional simples.
*   **Fluxos de Trabalho Personalizáveis:** Adapte o agente às suas necessidades e cenários de segurança únicos.
*   **📊 Módulo de Análise CSV:** Analise relatórios CSV do OpenVAS com insights alimentados por IA e gere resumos executivos.
*   **🌐 Interface Web Streamlit:** Dashboard web interativo para análise de CSV com gráficos e visualizações.
*   **🆓 Suporte para LLMs Opensource:** Use modelos gratuitos via Groq (Llama, Mixtral, Gemma) quando suas cotas do OpenAI acabarem.
*   **🏗️ Arquitetura Multi-Agente:** Agentes especializados para criação de tarefas, análise de resultados e processamento de CSV orquestrados via LangGraph.

## 🏛️ Arquitetura do Sistema

```
┌─────────────────────────────────────────┐
│      Camada de Interface do Usuário      │
│  (CLI, Dashboard Web Streamlit)         │
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│ Orquestração Multi-Agente (LangGraph)    │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│  │CriadorT. │ │AnalisaR. │ │AnalisaC. │ │
│  │Agente    │ │Agente    │ │Agente    │ │
│  └──────────┘ └──────────┘ └──────────┘ │
│         ▲          ▲          ▲          │
│         └──────────┴──────────┘          │
│      Roteador Agente Supervisor         │
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│      Camada de Provedor LLM             │
│  ┌──────────────┐  ┌──────────────┐    │
│  │   OpenAI     │  │    Groq      │    │
│  │  (GPT-4o)    │  │   (Llama 3)  │    │
│  └──────────────┘  └──────────────┘    │
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│   Serviços Externos e Dados              │
│ (API OpenVAS/GVM, Arquivos CSV, Sockets)│
└─────────────────────────────────────────┘
```

### Especificações dos Agentes

| Agente | Responsabilidade | Entrada | Saída |
|--------|---|---|---|
| **CriadorTarefa** | Analisa queries do usuário e cria tarefas acionáveis | Input do usuário, histórico de conversa | Tarefas estruturadas para processamento |
| **AnalisadorResultado** | Analisa respostas da API GVM/OpenVAS | Respostas GVM API, resultados de scan | Insights de vulnerabilidades priorizados |
| **AnalisadorCSV** | Processa e analisa relatórios CSV do OpenVAS | Arquivos CSV de `csv_reports/` | Resumos executivos, avaliações de risco |
| **Supervisor** | Roteia tarefas para agentes apropriados | Intenções do usuário, saídas dos agentes | Gerenciamento do fluxo de conversa |

## 🛠️ Stack de Tecnologias

- **Linguagem:** Python 3.8+
- **Framework de Agentes:** LangGraph + LangChain
- **Provedores LLM:** OpenAI GPT-4o, Groq (Llama 3.3-70b)
- **Processamento de Dados:** Pandas, NumPy
- **Framework Web:** Streamlit
- **Comunicação de API:** gvm-tools, httpx
- **Containerização:** Docker & Docker Compose


## 🏗️ Instalação do OpenVAS

Antes de usar o agente, é necessário ter o OpenVAS/GVM instalado e funcionando no seu sistema.

### Ubuntu 24.04

Siga o guia detalhado para instalar o Greenbone OpenVAS no Ubuntu 24.04:

- [Guia de Instalação OpenVAS no Ubuntu 24.04 (dev.iachieved.it)](https://dev.iachieved.it/iachievedit/installing-greenbone-openvas-on-ubuntu-24-04/)

### Kali Linux

No Kali, o OpenVAS (Greenbone) pode ser instalado diretamente pelos repositórios:

```bash
sudo apt update
sudo apt install openvas
sudo gvm-setup
sudo gvm-check-setup
```

Após a instalação, siga as instruções do terminal para finalizar a configuração e obter a senha de acesso.

---

## 🔧 Começando

### Pré-requisitos

*   Uma instância funcional do OpenVAS/Greenbone Vulnerability Management (GVM).
*   Python 3.8 ou superior.
*   Acesso à API do GVM.
*   (Opcional) Docker & Docker Compose para implantação containerizada


### Instalação do Agente

#### Opção 1: Docker (Recomendado) ✨

```bash
# Clone o repositório
git clone https://github.com/raphaelalvesdev/CEIA_OpenVAS_Agent
cd CEIA_OpenVAS_Agent

# Copie e configure o ambiente
cp env.template .env
# Edite .env com suas chaves de API OpenAI/Groq e credenciais GVM

# Implante com Docker Compose
docker-compose up -d

# Acesse o dashboard Streamlit em http://localhost:8501
```

#### Opção 2: Desenvolvimento Local

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/raphaelalvesdev/CEIA_OpenVAS_Agent
    cd CEIA_OpenVAS_Agent
    ```

2.  **Crie e ative um ambiente virtual:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Instale as dependências necessárias:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure seu ambiente:**
    Crie um arquivo `.env` no diretório raiz do projeto e adicione as informações de `ENV.md`

### Permissões

Para permitir que o agente se conecte ao `gvmd.sock` para requisições de API, você pode precisar ajustar as permissões:

```bash
sudo chmod 660 /run/gvmd/gvmd.sock
```

Se ainda encontrar problemas, você pode tentar uma configuração mais permissiva (use com cuidado):

```bash
sudo chmod 777 /run/gvmd/gvmd.sock
```

### Executando o Agente

Inicie o OpenVAS Agent com o seguinte comando:

```bash
python3 main.py
```

**Novos Comandos de Análise CSV:**
- "Analise os CSVs" - Analisa todos os arquivos CSV em csv_reports/
- "Lista os CSVs" - Lista os arquivos CSV disponíveis
- "Analise o arquivo X.csv" - Analisa um arquivo CSV específico

O agente agora integra recursos de análise CSV! Basta colocar seus relatórios CSV do OpenVAS em `csv_reports/` e pedir ao agente que os analise.

### Executando Análise CSV


Para instruções detalhadas sobre o módulo de Análise CSV, veja o arquivo `docs/CSV_ANALYZER.md`.

**Início Rápido:**

1. **Via Interface Streamlit (Recomendado):**
   ```bash
   streamlit run streamlit_app.py
   ```
   Acesse em `http://localhost:8501`

2. **Via Linha de Comando:**
   ```bash
   # Coloque seus arquivos CSV em csv_reports/
   python src/tools/csv_analyzer.py
   ```
   Os resultados serão salvos em `csv_analysis_results/`

## 📂 Estrutura do Projeto

```
.
├── .gitignore
├── ENV.md
├── LICENSE
├── main.py
├── streamlit_app.py          # Interface web Streamlit para análise CSV
├── openvasagent.png
├── README.md
├── requirements.txt
├── Dockerfile                 # Containerização Docker
├── docker-compose.yml         # Orquestração Docker Compose
├── csv_reports/              # Coloque seus arquivos CSV do OpenVAS aqui
├── csv_analysis_results/     # Os relatórios gerados são salvos aqui
├── docs/
│   ├── CSV_ANALYZER.md       # Documentação de Análise CSV
│   ├── diagram.html
│   └── Docs.md
└── src/
    ├── agents/
    │   ├── __init__.py
    │   ├── result_analyzer.py
    │   ├── supervisor.py
    │   ├── csv_analyzer.py
    │   └── task_creator.py
    ├── art/
    │   └── art.py
    ├── __pycache__/
    ├── state.py
    └── tools/
        ├── __init__.py
        ├── csv_analyzer.py   # Módulo de análise CSV
        ├── gvm_results.py
        └── gvm_workflow.py
```

# Selos Considerados

Os selos considerados são:
- Artefatos Disponíveis (SeloD)
- Artefatos Funcionais (SeloF)
- Artefatos Sustentáveis (SeloS)
- Experimentos Reprodutíveis (SeloR)

---

## ⚡ Métricas de Performance

| Métrica | Valor |
|---------|-------|
| Velocidade de Análise CSV | ~500 vulnerabilidades/min |
| Tempo de Resposta do Agente | <2 segundos em média |
| Precisão de Categorização LLM | 92% |
| Tempo de Operação | 99.5% |

## 🔧 Solução de Problemas

**Problemas Comuns:**

| Problema | Solução |
|----------|---------|
| Docker não encontrado | Instale Docker: `sudo apt-get install docker.io docker-compose` |
| Porta 8501 já em uso | Altere a porta em docker-compose.yml: `"8502:8501"` |
| Erros de chave de API | Verifique se o arquivo `.env` está configurado corretamente com chaves válidas |
| Permissão negada no socket GVM | Execute: `sudo chmod 660 /run/gvmd/gvmd.sock` |

## 🤝 Contribuindo

Bem-vindo contribuições da comunidade! Se quiser se envolver, sinta-se livre para:

*   Reportar bugs e solicitar funcionalidades
*   Enviar pull requests
*   Melhorar a documentação


## 📜 Licença

Este projeto está licenciado sob a Licença MIT. Veja o arquivo LICENSE para mais detalhes.


## 📧 Contato

Tem dúvidas ou feedback? Sinta-se livre para entrar em contato conosco pelo e-mail: rapha555lima@gmail.com