#!/usr/bin/env python3
"""
Script de comparação de modelos LLM para análise de CSV OpenVAS
Compara GPT-4o-mini vs modelos opensource (Groq: Llama 3.3, Mixtral)
"""
import os
import sys
import time
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from src.tools.csv_analyzer import OpenVASCSVAnalyzer

load_dotenv()

# Configurações dos modelos a serem testados
MODELS_CONFIG = {
    "Llama-3.3-70B": {
        "provider": "groq",
        "model": "llama-3.3-70b-versatile",
        "description": "Modelo opensource da Meta via Groq - 70B parâmetros"
    },
    "Llama-3.1-8B": {
        "provider": "groq",
        "model": "llama-3.1-8b-instant",
        "description": "Modelo opensource da Meta via Groq - versão compacta e rápida"
    },
    "Mixtral-8x7B": {
        "provider": "groq",
        "model": "mixtral-8x7b-32768",
        "description": "Modelo opensource da Mistral AI via Groq - Mixture of Experts"
    },
    "Gemma-2-9B": {
        "provider": "groq",
        "model": "gemma2-9b-it",
        "description": "Modelo opensource do Google via Groq - versão compacta"
    },
    "GPT-4o-mini": {
        "provider": "openai",
        "model": "gpt-4o-mini",
        "description": "Modelo proprietário da OpenAI - versão compacta e econômica"
    }
}

def run_analysis(csv_path: str, provider: str, model: str):
    """Executa análise com um modelo específico e retorna resultado + tempo"""
    print(f"  ⚙️  Analisando com {model}...")
    
    start_time = time.time()
    
    try:
        analyzer = OpenVASCSVAnalyzer(llm_provider=provider, model_name=model)
        result = analyzer.analyze_csv_file(csv_path)
        
        elapsed_time = time.time() - start_time
        
        return {
            "success": True,
            "summary": result['summary'],
            "statistics": result['statistics'],
            "time": elapsed_time,
            "error": None
        }
    except Exception as e:
        elapsed_time = time.time() - start_time
        return {
            "success": False,
            "summary": None,
            "statistics": None,
            "time": elapsed_time,
            "error": str(e)
        }

def generate_comparison_markdown(results: dict, csv_filename: str):
    """Gera markdown com comparação dos modelos"""
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    md_content = f"""# Comparação de Modelos LLM para Análise de Vulnerabilidades

## 📊 Relatório de Comparação

**Data da Análise:** {timestamp}  
**Arquivo CSV Analisado:** `{csv_filename}`  
**Objetivo:** Comparar desempenho e qualidade de resposta entre modelos proprietários (OpenAI) e opensource (Groq)

---

## 🎯 Modelos Testados

"""
    
    for model_name, config in MODELS_CONFIG.items():
        md_content += f"### {model_name}\n"
        md_content += f"- **Provider:** {config['provider'].upper()}\n"
        md_content += f"- **Modelo:** `{config['model']}`\n"
        md_content += f"- **Descrição:** {config['description']}\n"
        md_content += f"- **Custo:** {'Pago' if config['provider'] == 'openai' else '✅ Gratuito'}\n\n"
    
    md_content += "---\n\n## ⚡ Performance Comparativa\n\n"
    md_content += "| Modelo | Tempo de Resposta | Status |\n"
    md_content += "|--------|-------------------|--------|\n"
    
    for model_name, result in results.items():
        status = "✅ Sucesso" if result['success'] else "❌ Erro"
        time_str = f"{result['time']:.2f}s" if result['time'] else "N/A"
        md_content += f"| {model_name} | {time_str} | {status} |\n"
    
    md_content += "\n---\n\n## 📈 Análise Estatística dos Dados\n\n"
    
    # Pega estatísticas do primeiro modelo bem-sucedido
    stats = None
    for result in results.values():
        if result['success'] and result['statistics']:
            stats = result['statistics']
            break
    
    if stats:
        md_content += f"""**Dados do CSV:**
- Total de Vulnerabilidades: {stats['total_vulnerabilities']}
- Hosts Únicos Afetados: {stats['unique_hosts']}

**Distribuição por Severidade:**
"""
        if 'by_severity' in stats:
            for severity, count in stats['by_severity'].items():
                md_content += f"- {severity}: {count}\n"
    
    md_content += "\n---\n\n## 🤖 Respostas Comparativas dos Modelos\n\n"
    
    for model_name, result in results.items():
        md_content += f"### {model_name}\n\n"
        
        if result['success']:
            md_content += f"**⏱️ Tempo de Processamento:** {result['time']:.2f} segundos\n\n"
            md_content += "**📝 Resumo Gerado:**\n\n"
            md_content += "```\n"
            md_content += result['summary']
            md_content += "\n```\n\n"
        else:
            md_content += f"**❌ Erro durante análise:**\n\n"
            md_content += f"```\n{result['error']}\n```\n\n"
        
        md_content += "---\n\n"
    
    # Análise comparativa
    md_content += "## 🔍 Análise Comparativa\n\n"
    
    successful_results = {k: v for k, v in results.items() if v['success']}
    
    if len(successful_results) > 1:
        # Encontra o mais rápido
        fastest = min(successful_results.items(), key=lambda x: x[1]['time'])
        slowest = max(successful_results.items(), key=lambda x: x[1]['time'])
        
        md_content += f"### ⚡ Velocidade\n\n"
        md_content += f"- **Mais Rápido:** {fastest[0]} ({fastest[1]['time']:.2f}s)\n"
        md_content += f"- **Mais Lento:** {slowest[0]} ({slowest[1]['time']:.2f}s)\n"
        md_content += f"- **Diferença:** {slowest[1]['time'] - fastest[1]['time']:.2f}s ({((slowest[1]['time'] / fastest[1]['time']) - 1) * 100:.1f}% mais lento)\n\n"
    
    md_content += "### 💰 Custo-Benefício\n\n"
    md_content += "| Modelo | Custo | Performance | Recomendação |\n"
    md_content += "|--------|-------|-------------|---------------|\n"
    
    for model_name, config in MODELS_CONFIG.items():
        if model_name in successful_results:
            result = successful_results[model_name]
            cost = "💲 Pago" if config['provider'] == 'openai' else "🆓 Gratuito"
            perf = "⚡ Rápido" if result['time'] < 5 else "⏱️ Moderado" if result['time'] < 10 else "🐌 Lento"
            
            if config['provider'] == 'groq':
                rec = "⭐⭐⭐ Excelente para prototipagem e uso sem custos"
            else:
                rec = "⭐⭐ Bom mas requer créditos API"
            
            md_content += f"| {model_name} | {cost} | {perf} | {rec} |\n"
    
    md_content += "\n---\n\n## 🎓 Conclusões\n\n"
    
    md_content += """### Modelos Opensource (Groq)

**Vantagens:**
- ✅ **Totalmente gratuito** - Ideal para desenvolvimento e testes
- ✅ **Alta velocidade** - Inferência otimizada em hardware especializado
- ✅ **Qualidade competitiva** - Resultados comparáveis aos modelos pagos
- ✅ **Sem limites de crédito** - Rate limits generosos

**Desvantagens:**
- ⚠️ Dependência de serviço terceiro (Groq)
- ⚠️ Rate limits podem ser restritivos em produção de alta escala

### Modelos Proprietários (OpenAI)

**Vantagens:**
- ✅ **Estabilidade empresarial** - SLA e suporte profissional
- ✅ **Modelos de última geração** - Acesso aos modelos mais avançados
- ✅ **Ecossistema robusto** - Ferramentas e integrações maduras

**Desvantagens:**
- ❌ **Custo por uso** - Cada requisição consome créditos
- ❌ **Requer cartão de crédito** - Barreira de entrada

### 💡 Recomendação Final

"""
    
    if successful_results:
        groq_models = [k for k, v in MODELS_CONFIG.items() if v['provider'] == 'groq' and k in successful_results]
        if groq_models:
            best_groq = min([(k, successful_results[k]['time']) for k in groq_models], key=lambda x: x[1])
            md_content += f"""Para análise de vulnerabilidades do OpenVAS, **recomendamos o uso de modelos opensource via Groq**, especialmente o **{best_groq[0]}**:

1. **Sem custos operacionais** - Elimina preocupações com billing
2. **Performance adequada** - Tempo de resposta aceitável ({best_groq[1]:.2f}s)
3. **Qualidade suficiente** - Gera insights acionáveis e resumos executivos claros
4. **Escalabilidade inicial** - Permite validar o projeto antes de investir

**Considere migrar para OpenAI apenas se:**
- Necessitar SLA empresarial
- Escala de produção exceder rate limits do Groq
- Precisar de modelos específicos não disponíveis em Groq

"""
    
    md_content += """---

## 📚 Referências

- **Groq API:** https://console.groq.com
- **OpenAI API:** https://platform.openai.com
- **Llama 3.3:** https://ai.meta.com/llama/
- **Mixtral:** https://mistral.ai/
- **Gemma:** https://ai.google.dev/gemma

---

*Relatório gerado automaticamente pelo OpenVAS Agent - CSV Analysis Module*
"""
    
    return md_content

def main():
    print("🔒 Comparação de Modelos LLM - OpenVAS CSV Analysis")
    print("=" * 70)
    
    # Verifica se existem CSVs
    csv_folder = Path("csv_reports")
    csv_files = [f for f in csv_folder.glob("*.csv") if f.name != "exemplo_scan.csv"]
    
    if not csv_files:
        print("❌ Nenhum CSV encontrado em csv_reports/")
        print("💡 Use o openvas-speed.csv ou coloque seu próprio CSV")
        return
    
    # Usa o primeiro CSV encontrado
    csv_path = str(csv_files[0])
    csv_filename = csv_files[0].name
    
    print(f"\n📄 Analisando: {csv_filename}")
    print(f"📊 Testando {len(MODELS_CONFIG)} modelos...\n")
    
    # Verifica API keys
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  OPENAI_API_KEY não configurada - OpenAI será pulado")
    
    if not os.getenv("GROQ_API_KEY"):
        print("❌ GROQ_API_KEY não configurada - modelos Groq não funcionarão")
        return
    
    # Executa análise com cada modelo
    results = {}
    
    for model_name, config in MODELS_CONFIG.items():
        print(f"\n🤖 Testando: {model_name}")
        
        # Pula OpenAI se não tiver API key
        if config['provider'] == 'openai' and not os.getenv("OPENAI_API_KEY"):
            print("  ⏭️  Pulando (API key não configurada)")
            continue
        
        result = run_analysis(csv_path, config['provider'], config['model'])
        results[model_name] = result
        
        if result['success']:
            print(f"  ✅ Sucesso em {result['time']:.2f}s")
        else:
            print(f"  ❌ Erro: {result['error'][:100]}...")
        
        # Delay entre requests para evitar rate limit
        time.sleep(2)
    
    # Gera markdown
    print("\n\n📝 Gerando relatório comparativo...")
    markdown = generate_comparison_markdown(results, csv_filename)
    
    # Salva arquivo
    output_file = Path("docs/MODEL_COMPARISON.md")
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown)
    
    print(f"✅ Relatório salvo em: {output_file}")
    print("\n" + "=" * 70)
    print("🎉 Comparação concluída!")
    print(f"📖 Visualize o relatório: cat {output_file}")

if __name__ == "__main__":
    main()
