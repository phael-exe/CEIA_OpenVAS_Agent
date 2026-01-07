# 🎯 Comandos do Agente - CSV Analysis

## 📊 Análise de CSV Integrada ao Agente

O agente principal agora suporta análise de relatórios CSV do OpenVAS diretamente na conversa!

### Comandos Disponíveis

#### 📂 Listar CSVs
```
User: Lista os CSVs disponíveis
User: Quais arquivos CSV eu tenho?
User: Mostra os relatórios
```

#### 🔍 Analisar Todos os CSVs
```
User: Analise os CSVs
User: Faça análise dos relatórios CSV
User: Gera resumo dos CSVs
```

#### 📄 Analisar CSV Específico
```
User: Analise o arquivo openvas-speed.csv
User: Quero ver o relatório de scan_2024.csv
User: Analisa o CSV exemplo_scan.csv
```

### 💬 Fluxo de Conversa Exemplo

```
🤖 Using GROQ as LLM provider

User: Lista os CSVs

Processing...

Result: 📂 Arquivos CSV disponíveis (2):
  - exemplo_scan.csv (1.23 KB)
  - openvas-speed.csv (2.45 KB)

💡 Use 'analyze_csv_report' para analisar um arquivo específico ou todos.

Do you need anything else?

User: Analise todos

Processing...

Result: ✅ Análise de 2 arquivo(s) CSV concluída!

📄 exemplo_scan.csv
- Vulnerabilidades: 15
- Hosts: 6
- Críticas: 4
- Relatório: relatorio_exemplo_scan.txt

📄 openvas-speed.csv
- Vulnerabilidades: 42
- Hosts: 12
- Críticas: 8
- Relatório: relatorio_openvas-speed.txt

💡 Para visualização interativa, execute: streamlit run streamlit_app.py
📂 Todos os relatórios foram salvos em: csv_analysis_results/

Do you need anything else?

User: quit
```

### 🎨 Três Formas de Usar

#### 1️⃣ Via Agente Conversacional (Novo!)
```bash
python main.py
# Converse naturalmente: "analise os csvs", "lista relatórios", etc.
```

#### 2️⃣ Via Interface Streamlit
```bash
streamlit run streamlit_app.py
# Interface web com gráficos interativos
```

#### 3️⃣ Via Script Direto
```bash
python test_csv_analyzer.py
# Análise rápida via linha de comando
```

### 🤖 Modelos Suportados

Configure no `.env`:

**Groq (Gratuito):**
```bash
LLM_PROVIDER=groq
GROQ_API_KEY=gsk_sua_chave
GROQ_MODEL_ID=llama-3.3-70b-versatile
```

**OpenAI:**
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-sua_chave
OPENAI_MODEL_ID=gpt-4o-mini
```

### 🔄 Como Funciona

1. **Supervisor detecta** solicitação de análise de CSV
2. **Roteia para CSVAnalyzer** agent
3. **CSV Analyzer** processa os arquivos
4. **Gera análise com IA** (Groq ou OpenAI)
5. **Salva relatório** em csv_analysis_results/
6. **Retorna resumo** ao usuário

### 📁 Estrutura de Pastas

```
CEIA_OpenVAS_Agent/
├── csv_reports/          # 📥 Coloque seus CSVs aqui
│   ├── README.md         # ✅ Versionado
│   └── *.csv            # 🚫 Não versionado (gitignore)
├── csv_analysis_results/ # 📊 Relatórios gerados
│   └── *.txt            # 🚫 Não versionado
└── main.py              # 🤖 Agente principal
```

### 🔒 Segurança & Git

- ✅ Estrutura de pastas **é versionada**
- 🚫 Arquivos `.csv` **não são versionados** (privacidade)
- 🚫 Relatórios `.txt` **não são versionados** (privacidade)
- ✅ Código e documentação **são versionados**

### 💡 Dicas

1. **Coloque múltiplos CSVs** - o agente analisa todos de uma vez
2. **Use linguagem natural** - "analise", "lista", "mostra", etc.
3. **Relatórios persistem** - salvos em csv_analysis_results/
4. **Groq é gratuito** - troque de OpenAI se estiver sem créditos

### 🆘 Troubleshooting

**"Nenhum CSV encontrado"**
```bash
# Coloque arquivos .csv em:
cp seu_relatorio.csv csv_reports/
```

**"GROQ_API_KEY not found"**
```bash
# Configure no .env:
GROQ_API_KEY=gsk_sua_chave
LLM_PROVIDER=groq
```

**Erro de modelo**
```bash
# Atualize para modelo atual:
GROQ_MODEL_ID=llama-3.3-70b-versatile
```

---

**🎉 Agora você tem análise de CSV integrada diretamente no agente conversacional!**
