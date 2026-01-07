# 🎯 Início Rápido - Análise de CSV OpenVAS

## ⚡ Setup em 3 Minutos

### 1️⃣ Instale as Dependências
```bash
pip install langchain-groq streamlit plotly
```

### 2️⃣ Configure a API (Groq - GRATUITO)

1. Acesse https://console.groq.com e crie conta
2. Gere uma API Key
3. Adicione no `.env`:
   ```bash
   GROQ_API_KEY = 'gsk_sua_chave_aqui'
   LLM_PROVIDER = 'groq'
   ```

### 3️⃣ Execute!

**Opção A - Interface Web (Recomendado):**
```bash
streamlit run streamlit_app.py
```

**Opção B - Linha de Comando:**
```bash
# Coloque CSVs em csv_reports/
python test_csv_analyzer.py
```

---

## 📖 Guias Completos

- **[CSV_ANALYZER.md](CSV_ANALYZER.md)** - Documentação completa
- **[GROQ_SETUP.md](GROQ_SETUP.md)** - Como configurar Groq

---

## 💡 Exemplo de Uso

### Via Python
```python
from src.tools.csv_analyzer import OpenVASCSVAnalyzer

# Inicializa com Groq (gratuito)
analyzer = OpenVASCSVAnalyzer(
    llm_provider="groq",
    model_name="llama-3.1-70b-versatile"
)

# Analisa CSV
result = analyzer.analyze_csv_file("csv_reports/scan.csv")

# Exibe resumo
print(result['summary'])

# Salva relatório
analyzer.save_report(result, "relatorio.txt")
```

### Via Streamlit
1. Abra http://localhost:8501
2. Faça upload do CSV ou escolha da pasta
3. Visualize gráficos e análise da IA
4. Download do relatório

---

## 🎨 O que você vai ver

✅ Total de vulnerabilidades encontradas  
✅ Hosts afetados  
✅ Distribuição por severidade (Critical, High, Medium, Low)  
✅ Top 10 vulnerabilidades mais comuns  
✅ Hosts com mais problemas  
✅ Resumo executivo gerado por IA  
✅ Recomendações de remediação  
✅ Gráficos interativos  

---

## ❓ Problemas Comuns

### "No module named 'langchain_groq'"
```bash
pip install langchain-groq
```

### "GROQ_API_KEY not found"
Adicione a chave no arquivo `.env`

### CSV não é reconhecido
Certifique-se que tem colunas: IP/Host e Severity/CVSS

---

## 🆘 Precisa de Ajuda?

1. Veja os exemplos em `csv_reports/exemplo_scan.csv`
2. Leia [CSV_ANALYZER.md](CSV_ANALYZER.md)
3. Configure Groq: [GROQ_SETUP.md](GROQ_SETUP.md)

---

**Pronto para começar! 🚀**
