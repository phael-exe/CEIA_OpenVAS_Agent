"""
Agente de Análise de CSV do OpenVAS
"""
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import tool
from pathlib import Path
import os

from ..tools.csv_analyzer import OpenVASCSVAnalyzer
from ..state import AgentState


@tool
def analyze_csv_report(file_path: str = "") -> str:
    """
    Analisa relatórios CSV do OpenVAS e gera resumo executivo com IA.
    
    Args:
        file_path: Caminho do arquivo CSV. Se vazio, analisa todos os CSVs em csv_reports/
        
    Returns:
        Resumo da análise com estatísticas e insights
    """
    try:
        # Define provider e modelo
        llm_provider = os.getenv("LLM_PROVIDER", "groq")
        model_name = os.getenv("GROQ_MODEL_ID") if llm_provider == "groq" else os.getenv("OPENAI_MODEL_ID")
        
        analyzer = OpenVASCSVAnalyzer(llm_provider=llm_provider, model_name=model_name)
        
        if file_path and file_path.strip():
            # Analisa arquivo específico
            if not Path(file_path).exists():
                return f"❌ Arquivo não encontrado: {file_path}"
            
            result = analyzer.analyze_csv_file(file_path)
            
            # Salva relatório
            output_folder = Path("csv_analysis_results")
            output_folder.mkdir(exist_ok=True)
            output_file = output_folder / f"relatorio_{Path(file_path).stem}.txt"
            analyzer.save_report(result, str(output_file))
            
            stats = result['statistics']
            summary = f"""
📊 Análise do Relatório: {Path(file_path).name}
{'='*60}

📈 ESTATÍSTICAS:
- Total de Vulnerabilidades: {stats['total_vulnerabilities']}
- Hosts Afetados: {stats['unique_hosts']}
- Distribuição por Severidade: {stats.get('by_severity', {})}

🤖 RESUMO EXECUTIVO:
{result['summary']}

💾 Relatório completo salvo em: {output_file}
"""
            return summary
        
        else:
            # Analisa todos os CSVs da pasta
            csv_folder = Path("csv_reports")
            
            if not csv_folder.exists():
                csv_folder.mkdir()
                return "📁 Pasta csv_reports/ criada. Coloque seus arquivos CSV lá e tente novamente."
            
            csv_files = list(csv_folder.glob("*.csv"))
            
            if not csv_files:
                return "❌ Nenhum arquivo CSV encontrado em csv_reports/. Coloque seus relatórios do OpenVAS lá."
            
            results = []
            output_folder = Path("csv_analysis_results")
            output_folder.mkdir(exist_ok=True)
            
            for csv_file in csv_files:
                try:
                    result = analyzer.analyze_csv_file(str(csv_file))
                    stats = result['statistics']
                    
                    # Salva relatório
                    output_file = output_folder / f"relatorio_{csv_file.stem}.txt"
                    analyzer.save_report(result, str(output_file))
                    
                    results.append(f"""
📄 {csv_file.name}
- Vulnerabilidades: {stats['total_vulnerabilities']}
- Hosts: {stats['unique_hosts']}
- Críticas: {stats.get('by_severity', {}).get('Critical', 0)}
- Relatório: {output_file.name}
""")
                except Exception as e:
                    results.append(f"❌ Erro ao processar {csv_file.name}: {str(e)}")
            
            summary = f"""
✅ Análise de {len(csv_files)} arquivo(s) CSV concluída!

{''.join(results)}

💡 Para visualização interativa, execute: streamlit run streamlit_app.py
📂 Todos os relatórios foram salvos em: csv_analysis_results/
"""
            return summary
            
    except Exception as e:
        return f"❌ Erro na análise: {str(e)}\n\n💡 Dica: Verifique se o arquivo CSV tem o formato correto do OpenVAS."


@tool
def list_csv_reports() -> str:
    """
    Lista todos os arquivos CSV disponíveis para análise.
    
    Returns:
        Lista de arquivos CSV encontrados
    """
    csv_folder = Path("csv_reports")
    
    if not csv_folder.exists():
        csv_folder.mkdir()
        return "📁 Pasta csv_reports/ criada. Coloque seus arquivos CSV do OpenVAS lá."
    
    csv_files = list(csv_folder.glob("*.csv"))
    
    if not csv_files:
        return "❌ Nenhum arquivo CSV encontrado em csv_reports/."
    
    file_list = "\n".join([f"  - {f.name} ({f.stat().st_size / 1024:.2f} KB)" for f in csv_files])
    
    return f"""
📂 Arquivos CSV disponíveis ({len(csv_files)}):

{file_list}

💡 Use 'analyze_csv_report' para analisar um arquivo específico ou todos.
"""


def create_csv_analyzer_node():
    """Cria o nó do agente de análise de CSV."""
    tools = [analyze_csv_report, list_csv_reports]
    
    def csv_analyzer_agent(state: AgentState):
        """Agente que analisa relatórios CSV do OpenVAS."""
        messages = state['messages']
        last_message = messages[-1]
        
        # Verifica se é uma solicitação de análise de CSV
        content = last_message.content.lower()
        
        # Keywords para detectar solicitação de CSV
        csv_keywords = ['csv', 'relatório', 'relatorio', 'arquivo', 'planilha']
        analysis_keywords = ['analise', 'analisa', 'analisar', 'insights', 'resumo', 
                           'análise', 'report', 'avalia', 'verifica', 'mostra']
        list_keywords = ['listar', 'lista', 'quais', 'mostrar', 'ver', 'disponível', 
                        'disponivel', 'tem', 'existe']
        
        # Verifica se menciona CSV ou análise de relatórios
        has_csv = any(keyword in content for keyword in csv_keywords)
        has_analysis = any(keyword in content for keyword in analysis_keywords)
        has_list = any(keyword in content for keyword in list_keywords)
        
        # Se menciona CSV ou palavras de análise (covers "insights sobre o csv")
        if has_csv or has_analysis:
            if has_list and not has_analysis:
                # Lista arquivos disponíveis
                result = list_csv_reports.invoke({})
            else:
                # Analisa CSVs
                # Tenta extrair nome de arquivo da mensagem
                file_path = ""
                for word in last_message.content.split():
                    if '.csv' in word:
                        file_path = f"csv_reports/{word}" if not word.startswith('csv_reports/') else word
                        break
                
                result = analyze_csv_report.invoke({"file_path": file_path})
            
            # Retorna como ToolMessage para que o supervisor reconheça como fim
            return {"messages": [ToolMessage(content=result, tool_call_id="csv_analysis")]}
        
        return {"messages": [AIMessage(content="Não entendi. Você quer analisar um relatório CSV do OpenVAS?")]}
    
    return csv_analyzer_agent
