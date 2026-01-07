# 📊 Análise de CSV do OpenVAS

Este módulo permite analisar relatórios CSV exportados do OpenVAS usando IA para gerar resumos executivos claros e acionáveis.

## 🚀 Funcionalidades

- ✅ Análise de CSVs do OpenVAS com estatísticas detalhadas
- 🤖 Resumo inteligente usando IA (OpenAI ou Groq)
- 📈 Gráficos interativos de vulnerabilidades
- 💾 Export de relatórios em texto
- 🌐 Interface web com Streamlit
- 📁 Processamento em lote de múltiplos CSVs
- 🆓 Suporte a modelos opensource via Groq (GRATUITO!)

## 📦 Instalação

### 1. Instale as dependências adicionais

```bash
pip install langchain-groq streamlit plotly
```

Ou reinstale tudo:
```bash
pip install -r requirements.txt
```

### 2. Configure as credenciais

Adicione ao seu arquivo `.env`:

```bash
# Para usar Groq (GRATUITO - recomendado se está sem créditos OpenAI)
GROQ_API_KEY = 'sua_chave_groq'
GROQ_MODEL_ID = 'llama-3.1-70b-versatile'
LLM_PROVIDER = 'groq'

# OU para usar OpenAI
OPENAI_API_KEY = 'sua_chave_openai'
OPENAI_MODEL_ID = 'gpt-4o-mini'
LLM_PROVIDER = 'openai'
```

**💡 Como obter chave Groq (grátis):**
1. Acesse https://console.groq.com
2. Crie uma conta
3. Vá em API Keys e gere sua chave
4. Cole no `.env`

## 🎯 Modos de Uso

### Modo 1: Via Código (Pasta Local)

Ideal para processar CSVs diretamente da linha de comando.

#### Passo 1: Coloque os CSVs na pasta
```bash
mkdir csv_reports
# Copie seus arquivos .csv do OpenVAS para esta pasta
```

#### Passo 2: Execute o analisador
```bash
python src/tools/csv_analyzer.py
```

Os relatórios serão salvos em `csv_analysis_results/`

**Exemplo programático:**
```python
from src.tools.csv_analyzer import OpenVASCSVAnalyzer

# Usando Groq (gratuito)
analyzer = OpenVASCSVAnalyzer(llm_provider="groq", model_name="llama-3.1-70b-versatile")

# Analisa um CSV específico
result = analyzer.analyze_csv_file("csv_reports/scan_resultado.csv")

print(result['summary'])  # Resumo da IA
print(result['statistics'])  # Estatísticas detalhadas

# Salva relatório
analyzer.save_report(result, "relatorio_final.txt")
```

### Modo 2: Interface Streamlit (Recomendado)

Interface web interativa com gráficos e visualizações.

#### Inicie a aplicação:
```bash
streamlit run streamlit_app.py
```

Abrirá automaticamente no navegador: `http://localhost:8501`

#### Funcionalidades da Interface:

1. **Upload de Arquivo**
   - Faça upload direto de um CSV do OpenVAS
   - Visualização imediata com gráficos

2. **Pasta Local**
   - Analisa todos os CSVs de uma pasta
   - Processa múltiplos relatórios de uma vez

3. **Configurações**
   - Escolha entre OpenAI ou Groq
   - Selecione o modelo LLM
   - Visualize status da API Key

4. **Visualizações**
   - 📊 Distribuição por severidade
   - 🎯 Top vulnerabilidades
   - 💻 Hosts mais afetados
   - 📥 Download do relatório

## 📋 Formato do CSV

O analisador suporta CSVs com as seguintes colunas (flexível):

- `IP` ou `Host`: Endereço do host
- `Severity` ou `CVSS`: Nível de severidade
- `NVT Name` ou `Vulnerability`: Nome da vulnerabilidade
- Outras colunas são opcionais

**Exemplo de CSV do OpenVAS:**
```csv
IP,Port,Protocol,Severity,NVT Name,CVE
192.168.1.10,443,tcp,High,SSL/TLS: Report Weak Cipher Suites,CVE-2016-2183
192.168.1.10,22,tcp,Medium,SSH Weak Encryption Algorithms Supported,
192.168.1.20,80,tcp,Critical,Apache HTTP Server Multiple Vulnerabilities,CVE-2021-44790
```

## 🤖 Modelos Suportados

### Groq (Gratuito) ⭐ Recomendado
- `llama-3.1-70b-versatile` - Melhor balanço (padrão)
- `llama-3.1-8b-instant` - Mais rápido
- `llama-3.2-90b-text-preview` - Mais poderoso
- `mixtral-8x7b-32768` - Grande contexto
- `gemma2-9b-it` - Leve e eficiente

### OpenAI
- `gpt-4o` - Mais avançado
- `gpt-4o-mini` - Barato e rápido (padrão)
- `gpt-4-turbo` - Bom balanço
- `gpt-3.5-turbo` - Econômico

## 📊 Exemplo de Saída

```
================================================================================
RELATÓRIO DE ANÁLISE DE VULNERABILIDADES - OPENVAS
================================================================================

📊 RESUMO EXECUTIVO
Foram identificadas 127 vulnerabilidades em 15 hosts da rede, com 23 críticas 
e 45 de severidade alta requerendo ação imediata.

🎯 PRINCIPAIS DESCOBERTAS
- 23 vulnerabilidades CRÍTICAS detectadas
- 45 vulnerabilidades de ALTA severidade
- 3 hosts com mais de 20 vulnerabilidades cada
- Principais problemas: SSL/TLS weak ciphers, outdated software

📈 ANÁLISE DE RISCO
- Critical: 18% (ação imediata)
- High: 35% (prioridade alta)
- Medium: 32% (remediar em breve)
- Low: 15% (monitorar)

🔥 TOP PRIORIDADES
1. Atualizar Apache HTTP Server (CVE-2021-44790)
2. Desabilitar ciphers fracos em SSL/TLS
3. Atualizar OpenSSH em 8 servidores
4. Aplicar patches de segurança do kernel
5. Remover serviços obsoletos expostos

💡 RECOMENDAÇÕES
- Priorizar vulnerabilidades críticas nos próximos 7 dias
- Implementar política de patch management
- Realizar scan quinzenal
- Revisar configurações de firewall
```

## 🛠️ Solução de Problemas

### Erro: "No module named 'langchain_groq'"
```bash
pip install langchain-groq
```

### Erro: "GROQ_API_KEY not found"
Certifique-se de ter adicionado a chave no `.env`:
```bash
GROQ_API_KEY = 'gsk_...'
```

### CSV não é reconhecido
Verifique se o CSV tem pelo menos as colunas básicas (IP/Host e Severity/CVSS)

## 💡 Dicas

1. **Use Groq para economia**: Totalmente gratuito e rápido
2. **Processe múltiplos CSVs**: Coloque todos na pasta `csv_reports/`
3. **Compare scans**: Mantenha histórico de relatórios
4. **Personalize prompts**: Edite o SystemMessage em `csv_analyzer.py` para mudar estilo do relatório

## 📁 Estrutura de Arquivos

```
CEIA_OpenVAS_Agent/
├── csv_reports/              # Cole seus CSVs aqui
│   ├── scan_2024_01.csv
│   └── scan_2024_02.csv
├── csv_analysis_results/     # Relatórios gerados aqui
│   ├── relatorio_scan_2024_01.txt
│   └── relatorio_scan_2024_02.txt
├── src/tools/
│   └── csv_analyzer.py       # Módulo principal
├── streamlit_app.py          # Interface web
└── .env                      # Configurações
```

## 🎨 Screenshots da Interface

A interface Streamlit oferece:
- Métricas em cards coloridos
- Gráficos de barras interativos (Plotly)
- Filtros e configurações no sidebar
- Download de relatórios
- Suporte a tema claro/escuro

## 📝 Notas

- Os relatórios são salvos em formato texto (.txt) para fácil compartilhamento
- A análise usa IA para gerar insights contextualizados
- Gráficos são interativos e podem ser exportados como imagem
- Suporta processamento em lote para múltiplos scans

---

**Feito com ❤️ para facilitar a análise de vulnerabilidades**
