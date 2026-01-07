"""
Interface Streamlit para análise de relatórios CSV do OpenVAS
"""
import streamlit as st
import pandas as pd
import os
from pathlib import Path
import sys
from io import StringIO
import plotly.express as px
import plotly.graph_objects as go

# Adiciona o diretório raiz ao path
sys.path.append(str(Path(__file__).parent))

from src.tools.csv_analyzer import OpenVASCSVAnalyzer


def create_severity_chart(stats):
    """Cria gráfico de distribuição de severidade"""
    if 'by_severity' in stats:
        df = pd.DataFrame(list(stats['by_severity'].items()), 
                         columns=['Severidade', 'Quantidade'])
        
        # Cores para cada severidade
        color_map = {
            'Critical': '#d32f2f',
            'High': '#f57c00',
            'Medium': '#fbc02d',
            'Low': '#388e3c',
            'Info': '#1976d2',
            'Unknown': '#757575'
        }
        
        df['Color'] = df['Severidade'].map(color_map)
        
        fig = px.bar(df, x='Severidade', y='Quantidade', 
                    color='Severidade',
                    color_discrete_map=color_map,
                    title='Distribuição de Vulnerabilidades por Severidade')
        return fig
    return None


def create_top_vulnerabilities_chart(stats):
    """Cria gráfico de top vulnerabilidades"""
    if 'top_vulnerabilities' in stats:
        items = list(stats['top_vulnerabilities'].items())[:10]
        df = pd.DataFrame(items, columns=['Vulnerabilidade', 'Ocorrências'])
        
        # Trunca nomes longos
        df['Vulnerabilidade'] = df['Vulnerabilidade'].apply(
            lambda x: x[:50] + '...' if len(str(x)) > 50 else x
        )
        
        fig = px.bar(df, y='Vulnerabilidade', x='Ocorrências',
                    orientation='h',
                    title='Top 10 Vulnerabilidades Mais Comuns')
        fig.update_layout(yaxis={'categoryorder':'total ascending'})
        return fig
    return None


def create_hosts_chart(stats):
    """Cria gráfico de hosts mais afetados"""
    if 'most_affected_hosts' in stats:
        items = list(stats['most_affected_hosts'].items())[:10]
        df = pd.DataFrame(items, columns=['Host', 'Vulnerabilidades'])
        
        fig = px.bar(df, x='Host', y='Vulnerabilidades',
                    title='Hosts Mais Afetados (Top 10)')
        fig.update_xaxes(tickangle=45)
        return fig
    return None


def main():
    st.set_page_config(
        page_title="OpenVAS CSV Analyzer",
        page_icon="🔒",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🔒 Analisador de Relatórios OpenVAS")
    st.markdown("Análise inteligente de vulnerabilidades com IA")
    
    # Sidebar - Configurações
    with st.sidebar:
        st.header("⚙️ Configurações")
        
        # Seleção do provider LLM
        llm_provider = st.selectbox(
            "🤖 Provedor LLM",
            options=["openai", "groq"],
            help="Escolha entre OpenAI ou Groq (modelos opensource)"
        )
        
        # Seleção do modelo
        if llm_provider == "openai":
            model_options = ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"]
            default_model = os.getenv("OPENAI_MODEL_ID", "gpt-4o-mini")
        else:
            model_options = [
                "llama-3.3-70b-versatile",
                "llama-3.1-8b-instant",
                "llama-3.3-70b-specdec",
                "mixtral-8x7b-32768",
                "gemma2-9b-it"
            ]
            default_model = os.getenv("GROQ_MODEL_ID", "llama-3.3-70b-versatile")
        
        model_name = st.selectbox(
            "📊 Modelo",
            options=model_options,
            index=0 if default_model not in model_options else model_options.index(default_model)
        )
        
        st.markdown("---")
        
        # Informações de API Key
        if llm_provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                st.success("✅ OpenAI API Key configurada")
            else:
                st.error("❌ Configure OPENAI_API_KEY no .env")
        else:
            api_key = os.getenv("GROQ_API_KEY")
            if api_key:
                st.success("✅ Groq API Key configurada")
            else:
                st.error("❌ Configure GROQ_API_KEY no .env")
                st.info("💡 Obtenha gratuitamente em: https://console.groq.com")
        
        st.markdown("---")
        st.markdown("### 📖 Sobre")
        st.markdown("""
        Esta ferramenta analisa relatórios CSV do OpenVAS e gera resumos executivos usando IA.
        
        **Recursos:**
        - 📊 Estatísticas detalhadas
        - 🤖 Análise com IA
        - 📈 Gráficos interativos
        - 💾 Export de relatórios
        """)
    
    # Área principal
    st.markdown("---")
    
    # Tabs para diferentes modos de entrada
    tab1, tab2 = st.tabs(["📤 Upload de Arquivo", "📁 Pasta Local"])
    
    with tab1:
        st.markdown("### Upload do CSV do OpenVAS")
        uploaded_file = st.file_uploader(
            "Escolha um arquivo CSV",
            type=['csv'],
            help="Faça upload do relatório CSV exportado do OpenVAS"
        )
        
        if uploaded_file is not None:
            process_uploaded_file(uploaded_file, llm_provider, model_name)
    
    with tab2:
        st.markdown("### Análise de Pasta Local")
        st.info("📁 Coloque seus arquivos CSV na pasta `csv_reports/` no diretório do projeto")
        
        folder_path = st.text_input(
            "Caminho da pasta",
            value="csv_reports",
            help="Pasta contendo os arquivos CSV do OpenVAS"
        )
        
        if st.button("🔍 Analisar Pasta", type="primary"):
            process_folder(folder_path, llm_provider, model_name)


def process_uploaded_file(uploaded_file, llm_provider, model_name):
    """Processa arquivo enviado via upload"""
    try:
        # Salva temporariamente
        temp_path = Path("temp_csv") / uploaded_file.name
        temp_path.parent.mkdir(exist_ok=True)
        
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Análise
        with st.spinner(f"🔄 Analisando com {llm_provider.upper()} ({model_name})..."):
            analyzer = OpenVASCSVAnalyzer(llm_provider=llm_provider, model_name=model_name)
            analysis = analyzer.analyze_csv_file(str(temp_path))
        
        # Exibe resultados
        display_results(analysis, uploaded_file.name)
        
        # Limpa arquivo temporário
        temp_path.unlink()
        
    except Exception as e:
        st.error(f"❌ Erro ao processar arquivo: {str(e)}")
        st.exception(e)


def process_folder(folder_path, llm_provider, model_name):
    """Processa todos os CSVs de uma pasta"""
    folder = Path(folder_path)
    
    if not folder.exists():
        st.error(f"❌ Pasta não encontrada: {folder_path}")
        return
    
    csv_files = list(folder.glob("*.csv"))
    
    if not csv_files:
        st.warning(f"⚠️ Nenhum arquivo CSV encontrado em {folder_path}")
        return
    
    st.success(f"✅ Encontrados {len(csv_files)} arquivo(s) CSV")
    
    # Processa cada arquivo
    for idx, csv_file in enumerate(csv_files):
        st.markdown(f"### 📄 Arquivo {idx+1}/{len(csv_files)}: {csv_file.name}")
        
        try:
            with st.spinner(f"🔄 Analisando..."):
                analyzer = OpenVASCSVAnalyzer(llm_provider=llm_provider, model_name=model_name)
                analysis = analyzer.analyze_csv_file(str(csv_file))
            
            display_results(analysis, csv_file.name)
            st.markdown("---")
            
        except Exception as e:
            st.error(f"❌ Erro ao processar {csv_file.name}: {str(e)}")


def display_results(analysis, filename):
    """Exibe os resultados da análise"""
    stats = analysis['statistics']
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total de Vulnerabilidades", stats['total_vulnerabilities'])
    
    with col2:
        st.metric("Hosts Afetados", stats['unique_hosts'])
    
    with col3:
        critical_count = stats.get('by_severity', {}).get('Critical', 0)
        st.metric("Críticas", critical_count, delta=None, delta_color="inverse")
    
    with col4:
        high_count = stats.get('by_severity', {}).get('High', 0)
        st.metric("Altas", high_count, delta=None, delta_color="inverse")
    
    # Resumo da IA
    st.markdown("### 🤖 Análise Inteligente")
    with st.container():
        st.markdown(analysis['summary'])
    
    # Gráficos
    st.markdown("### 📊 Visualizações")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig1 = create_severity_chart(stats)
        if fig1:
            st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        fig2 = create_hosts_chart(stats)
        if fig2:
            st.plotly_chart(fig2, use_container_width=True)
    
    fig3 = create_top_vulnerabilities_chart(stats)
    if fig3:
        st.plotly_chart(fig3, use_container_width=True)
    
    # Botão de download do relatório
    st.markdown("### 💾 Exportar Relatório")
    
    report_text = f"""
{'='*80}
RELATÓRIO DE ANÁLISE DE VULNERABILIDADES - OPENVAS
Arquivo: {filename}
{'='*80}

{analysis['summary']}

{'='*80}
ESTATÍSTICAS DETALHADAS
{'='*80}

Total de Vulnerabilidades: {stats['total_vulnerabilities']}
Hosts Únicos: {stats['unique_hosts']}

Distribuição por Severidade:
{pd.Series(stats.get('by_severity', {})).to_string()}

Top Vulnerabilidades:
{pd.Series(stats.get('top_vulnerabilities', {})).to_string()}

Hosts Mais Afetados:
{pd.Series(stats.get('most_affected_hosts', {})).to_string()}
"""
    
    st.download_button(
        label="📥 Download Relatório (TXT)",
        data=report_text,
        file_name=f"relatorio_{Path(filename).stem}.txt",
        mime="text/plain"
    )


if __name__ == "__main__":
    main()
