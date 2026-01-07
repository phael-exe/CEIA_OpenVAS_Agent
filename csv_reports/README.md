# 📂 CSV Reports Folder

Esta pasta é usada para armazenar relatórios CSV exportados do OpenVAS.

## 📝 Como usar

1. **Exporte seu relatório do OpenVAS em formato CSV**
2. **Coloque o arquivo .csv nesta pasta**
3. **Execute a análise**:
   - Via agente: `python main.py` e peça "analise os CSVs"
   - Via script: `python test_csv_analyzer.py`
   - Via interface: `streamlit run streamlit_app.py`

## 🔒 Privacidade

Por segurança, **todos os arquivos .csv desta pasta são ignorados pelo Git** e não serão versionados.

Apenas este README é versionado para manter a estrutura de pastas.

## 📊 Exemplo

Um arquivo de exemplo está incluído: `exemplo_scan.csv`

## 💡 Dica

Os relatórios gerados serão salvos em `csv_analysis_results/`
