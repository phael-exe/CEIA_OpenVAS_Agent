"""
Módulo para análise de relatórios CSV do OpenVAS
Suporta tanto OpenAI quanto modelos opensource (Groq)
"""
import os
import pandas as pd
from typing import Dict, List, Optional
from pathlib import Path
import json

# Imports condicionais para suportar diferentes providers
try:
    from langchain_openai import ChatOpenAI
except ImportError:
    ChatOpenAI = None

try:
    from langchain_groq import ChatGroq
except ImportError:
    ChatGroq = None

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate


class OpenVASCSVAnalyzer:
    """Analisador de relatórios CSV do OpenVAS com suporte a múltiplos modelos LLM"""
    
    def __init__(self, llm_provider: str = "openai", model_name: Optional[str] = None):
        """
        Inicializa o analisador
        
        Args:
            llm_provider: "openai" ou "groq" 
            model_name: Nome do modelo (ex: "gpt-4o", "llama-3.1-70b-versatile")
        """
        self.llm_provider = llm_provider.lower()
        self.llm = self._initialize_llm(model_name)
        
    def _initialize_llm(self, model_name: Optional[str]):
        """Inicializa o modelo LLM baseado no provider"""
        if self.llm_provider == "openai":
            if ChatOpenAI is None:
                raise ImportError("langchain-openai não está instalado")
            return ChatOpenAI(
                model=model_name or os.getenv("OPENAI_MODEL_ID", "gpt-4o-mini"),
                temperature=0
            )
        elif self.llm_provider == "groq":
            if ChatGroq is None:
                raise ImportError("langchain-groq não está instalado. Instale com: pip install langchain-groq")
            return ChatGroq(
                model=model_name or os.getenv("GROQ_MODEL_ID", "llama-3.3-70b-versatile"),
                temperature=0,
                api_key=os.getenv("GROQ_API_KEY")
            )
        else:
            raise ValueError(f"Provider não suportado: {self.llm_provider}. Use 'openai' ou 'groq'")
    
    def load_csv(self, file_path: str) -> pd.DataFrame:
        """Carrega o arquivo CSV do OpenVAS"""
        try:
            df = pd.read_csv(file_path)
            return df
        except Exception as e:
            raise Exception(f"Erro ao carregar CSV: {str(e)}")
    
    def get_vulnerability_statistics(self, df: pd.DataFrame) -> Dict:
        """Extrai estatísticas básicas das vulnerabilidades"""
        stats = {
            "total_vulnerabilities": len(df),
            "unique_hosts": df['IP'].nunique() if 'IP' in df.columns else df['Host'].nunique() if 'Host' in df.columns else 0,
        }
        
        # Análise por severidade
        if 'Severity' in df.columns:
            stats['by_severity'] = df['Severity'].value_counts().to_dict()
        elif 'CVSS' in df.columns:
            # Mapeia CVSS para severidade
            df['Severity_Level'] = df['CVSS'].apply(self._cvss_to_severity)
            stats['by_severity'] = df['Severity_Level'].value_counts().to_dict()
        
        # Top vulnerabilidades
        if 'NVT Name' in df.columns:
            stats['top_vulnerabilities'] = df['NVT Name'].value_counts().head(10).to_dict()
        elif 'Vulnerability' in df.columns:
            stats['top_vulnerabilities'] = df['Vulnerability'].value_counts().head(10).to_dict()
        
        # Hosts mais afetados
        host_col = 'IP' if 'IP' in df.columns else 'Host' if 'Host' in df.columns else None
        if host_col:
            stats['most_affected_hosts'] = df[host_col].value_counts().head(10).to_dict()
        
        return stats
    
    def _cvss_to_severity(self, cvss_score: float) -> str:
        """Converte score CVSS para nível de severidade"""
        try:
            score = float(cvss_score)
            if score >= 9.0:
                return "Critical"
            elif score >= 7.0:
                return "High"
            elif score >= 4.0:
                return "Medium"
            elif score > 0:
                return "Low"
            else:
                return "Info"
        except:
            return "Unknown"
    
    def generate_summary(self, df: pd.DataFrame, stats: Dict) -> str:
        """Gera um resumo detalhado usando o LLM"""
        
        # Prepara dados para o LLM
        data_summary = f"""
Estatísticas do Relatório OpenVAS:

Total de Vulnerabilidades: {stats['total_vulnerabilities']}
Hosts Únicos Afetados: {stats['unique_hosts']}

Distribuição por Severidade:
{json.dumps(stats.get('by_severity', {}), indent=2)}

Top 10 Vulnerabilidades Mais Comuns:
{json.dumps(stats.get('top_vulnerabilities', {}), indent=2)}

Hosts Mais Afetados:
{json.dumps(stats.get('most_affected_hosts', {}), indent=2)}
"""
        
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""Você é um especialista em segurança cibernética analisando relatórios de vulnerabilidades do OpenVAS.
Sua tarefa é criar um relatório executivo claro, objetivo e acionável em português brasileiro.

Estruture o relatório da seguinte forma:
1. 📊 RESUMO EXECUTIVO - Visão geral em 2-3 frases
2. 🎯 PRINCIPAIS DESCOBERTAS - Pontos críticos que precisam de atenção imediata
3. 📈 ANÁLISE DE RISCO - Distribuição e impacto das vulnerabilidades
4. 🔥 TOP PRIORIDADES - 5 itens mais urgentes para remediar
5. 💡 RECOMENDAÇÕES - Próximos passos práticos

Use emojis para facilitar a leitura e seja direto ao ponto."""),
            HumanMessage(content=data_summary)
        ])
        
        response = self.llm.invoke(prompt.format_messages())
        return response.content
    
    def analyze_csv_file(self, csv_path: str) -> Dict:
        """
        Análise completa de um arquivo CSV do OpenVAS
        
        Returns:
            Dict com 'statistics', 'summary' e 'raw_data'
        """
        # Carrega e analisa
        df = self.load_csv(csv_path)
        stats = self.get_vulnerability_statistics(df)
        summary = self.generate_summary(df, stats)
        
        return {
            "statistics": stats,
            "summary": summary,
            "raw_data": df.to_dict('records')[:100]  # Limita para não sobrecarregar
        }
    
    def save_report(self, analysis: Dict, output_path: str):
        """Salva o relatório em arquivo texto"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("RELATÓRIO DE ANÁLISE DE VULNERABILIDADES - OPENVAS\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(analysis['summary'])
            f.write("\n\n")
            
            f.write("=" * 80 + "\n")
            f.write("ESTATÍSTICAS DETALHADAS\n")
            f.write("=" * 80 + "\n\n")
            f.write(json.dumps(analysis['statistics'], indent=2, ensure_ascii=False))


def analyze_from_folder(folder_path: str = "csv_reports", 
                        output_folder: str = "csv_analysis_results",
                        llm_provider: str = "openai",
                        model_name: Optional[str] = None):
    """
    Analisa todos os arquivos CSV em uma pasta
    
    Args:
        folder_path: Pasta com os CSVs do OpenVAS
        output_folder: Pasta para salvar os relatórios
        llm_provider: "openai" ou "groq"
        model_name: Nome do modelo específico
    """
    folder = Path(folder_path)
    output = Path(output_folder)
    output.mkdir(exist_ok=True)
    
    analyzer = OpenVASCSVAnalyzer(llm_provider=llm_provider, model_name=model_name)
    
    csv_files = list(folder.glob("*.csv"))
    
    if not csv_files:
        print(f"❌ Nenhum arquivo CSV encontrado em {folder_path}")
        return
    
    print(f"📁 Encontrados {len(csv_files)} arquivo(s) CSV")
    
    for csv_file in csv_files:
        print(f"\n⚙️  Analisando: {csv_file.name}")
        try:
            analysis = analyzer.analyze_csv_file(str(csv_file))
            
            # Salva relatório
            output_file = output / f"relatorio_{csv_file.stem}.txt"
            analyzer.save_report(analysis, str(output_file))
            
            print(f"✅ Relatório salvo em: {output_file}")
            print(f"\n{analysis['summary'][:200]}...\n")
            
        except Exception as e:
            print(f"❌ Erro ao processar {csv_file.name}: {str(e)}")


if __name__ == "__main__":
    # Exemplo de uso direto
    print("🚀 Analisador de CSV OpenVAS")
    print("=" * 60)
    
    # Verifica se a pasta existe
    if not Path("csv_reports").exists():
        Path("csv_reports").mkdir()
        print("📁 Pasta 'csv_reports' criada. Coloque seus CSVs lá!")
    else:
        analyze_from_folder(
            folder_path="csv_reports",
            output_folder="csv_analysis_results",
            llm_provider=os.getenv("LLM_PROVIDER", "openai")
        )
