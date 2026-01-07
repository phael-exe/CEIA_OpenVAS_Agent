#!/usr/bin/env python3
"""
Script de teste rápido para o módulo CSV Analyzer
"""
import os
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
from src.tools.csv_analyzer import OpenVASCSVAnalyzer

# Carrega variáveis de ambiente
load_dotenv()

def main():
    print("🔒 Teste do Analisador CSV OpenVAS")
    print("=" * 60)
    
    # Verifica se existe CSV de exemplo
    csv_path = "csv_reports/exemplo_scan.csv"
    
    if not Path(csv_path).exists():
        print(f"❌ Arquivo de exemplo não encontrado: {csv_path}")
        print("💡 Coloque um arquivo CSV do OpenVAS em csv_reports/")
        return
    
    # Pergunta qual provider usar
    print("\n🤖 Escolha o provedor LLM:")
    print("1. Groq (gratuito - recomendado)")
    print("2. OpenAI")
    
    choice = input("\nEscolha (1 ou 2) [1]: ").strip() or "1"
    
    if choice == "1":
        provider = "groq"
        # Verifica se tem API key
        if not os.getenv("GROQ_API_KEY"):
            print("\n❌ GROQ_API_KEY não configurada no .env")
            print("💡 Obtenha grátis em: https://console.groq.com")
            return
        print(f"✅ Usando Groq com modelo: {os.getenv('GROQ_MODEL_ID', 'llama-3.3-70b-versatile')}")
    else:
        provider = "openai"
        if not os.getenv("OPENAI_API_KEY"):
            print("\n❌ OPENAI_API_KEY não configurada no .env")
            return
        print(f"✅ Usando OpenAI com modelo: {os.getenv('OPENAI_MODEL_ID', 'gpt-4o-mini')}")
    
    print(f"\n⚙️  Analisando: {csv_path}")
    print("⏳ Aguarde...\n")
    
    try:
        # Cria o analisador
        analyzer = OpenVASCSVAnalyzer(llm_provider=provider)
        
        # Analisa o CSV
        result = analyzer.analyze_csv_file(csv_path)
        
        # Exibe resultados
        print("=" * 60)
        print("📊 ESTATÍSTICAS")
        print("=" * 60)
        stats = result['statistics']
        print(f"Total de Vulnerabilidades: {stats['total_vulnerabilities']}")
        print(f"Hosts Únicos: {stats['unique_hosts']}")
        
        if 'by_severity' in stats:
            print("\nDistribuição por Severidade:")
            for severity, count in stats['by_severity'].items():
                print(f"  {severity}: {count}")
        
        print("\n" + "=" * 60)
        print("🤖 ANÁLISE DA IA")
        print("=" * 60)
        print(result['summary'])
        
        # Salva relatório
        output_path = "csv_analysis_results/teste_relatorio.txt"
        Path("csv_analysis_results").mkdir(exist_ok=True)
        analyzer.save_report(result, output_path)
        
        print("\n" + "=" * 60)
        print(f"✅ Relatório completo salvo em: {output_path}")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Erro durante análise: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
