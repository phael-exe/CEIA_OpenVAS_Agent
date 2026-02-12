#!/usr/bin/env python3
"""
Comparação rápida de modelos LLM - Versão simplificada
Usa o exemplo_scan.csv que é menor para análise mais rápida
"""
import os
import sys
import time
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent))
from src.tools.csv_analyzer import OpenVASCSVAnalyzer

load_dotenv()

# Modelos principais para comparação
MODELS = {
    "Llama-3.3-70B (Groq)": {"provider": "groq", "model": "llama-3.3-70b-versatile"},
    "Mixtral-8x7B (Groq)": {"provider": "groq", "model": "mixtral-8x7b-32768"},
}

def main():
    print("🚀 Comparação Rápida de Modelos LLM\n")
    
    csv_path = "csv_reports/exemplo_scan.csv"
    
    if not Path(csv_path).exists():
        print(f"❌ Arquivo não encontrado: {csv_path}")
        return
    
    results = {}
    
    for model_name, config in MODELS.items():
        print(f"\n📊 Testando: {model_name}")
        start = time.time()
        
        try:
            analyzer = OpenVASCSVAnalyzer(config['provider'], config['model'])
            result = analyzer.analyze_csv_file(csv_path)
            elapsed = time.time() - start
            
            results[model_name] = {
                "success": True,
                "summary": result['summary'],
                "stats": result['statistics'],
                "time": elapsed
            }
            print(f"✅ Concluído em {elapsed:.2f}s")
            
        except Exception as e:
            elapsed = time.time() - start
            results[model_name] = {
                "success": False,
                "error": str(e),
                "time": elapsed
            }
            print(f"❌ Erro: {str(e)[:100]}")
        
        time.sleep(2)
    
    # Gera markdown
    md = f"""# Comparação de Modelos LLM para Análise de Vulnerabilidades OpenVAS

**Data:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Arquivo Analisado:** `{Path(csv_path).name}`

## 📊 Modelos Testados

"""
    
    for model_name, config in MODELS.items():
        provider = config['provider'].upper()
        md += f"### {model_name}\n"
        md += f"- **Provider:** {provider}\n"
        md += f"- **Modelo:** `{config['model']}`\n"
        md += f"- **Custo:** {'💰 Pago' if provider == 'OPENAI' else '🆓 Gratuito'}\n\n"
    
    md += "## ⚡ Performance\n\n"
    md += "| Modelo | Tempo | Status |\n|--------|-------|--------|\n"
    
    for name, result in results.items():
        status = "✅" if result['success'] else "❌"
        time_str = f"{result['time']:.2f}s"
        md += f"| {name} | {time_str} | {status} |\n"
    
    # Estatísticas (pega do primeiro sucesso)
    stats = next((r['stats'] for r in results.values() if r['success']), None)
    if stats:
        md += f"\n## 📈 Dados Analisados\n\n"
        md += f"- **Total de Vulnerabilidades:** {stats['total_vulnerabilities']}\n"
        md += f"- **Hosts Afetados:** {stats['unique_hosts']}\n"
        
        if 'by_severity' in stats:
            md += f"\n**Distribuição por Severidade:**\n"
            for sev, count in stats['by_severity'].items():
                md += f"- {sev}: {count}\n"
    
    md += "\n## 🤖 Respostas Geradas\n\n"
    
    for name, result in results.items():
        md += f"### {name}\n\n"
        if result['success']:
            md += f"**⏱️ Tempo:** {result['time']:.2f}s\n\n"
            md += "**Resumo:**\n\n```\n"
            md += result['summary']
            md += "\n```\n\n---\n\n"
        else:
            md += f"**❌ Erro:** {result.get('error', 'Desconhecido')}\n\n---\n\n"
    
    md += """## 💡 Conclusões

### Modelos Opensource (Groq)

**Vantagens:**
- ✅ Totalmente gratuito
- ✅ Alta velocidade de inferência
- ✅ Qualidade competitiva para análise de vulnerabilidades
- ✅ Sem necessidade de billing/cartão de crédito

**Recomendação:**
Para análise de relatórios OpenVAS, modelos opensource via Groq são **ideais** para:
- Prototipagem e desenvolvimento
- Uso sem custos operacionais
- Análises rápidas e iterativas
- Validação de conceito antes de investir em APIs pagas

### Quando Considerar OpenAI

- SLA empresarial necessário
- Escala de produção além dos rate limits gratuitos
- Necessidade de modelos específicos (GPT-4, etc.)

---

*Relatório gerado automaticamente pelo OpenVAS Agent*
"""
    
    # Salva
    output = Path("docs/MODEL_COMPARISON.md")
    output.parent.mkdir(exist_ok=True)
    output.write_text(md, encoding='utf-8')
    
    print(f"\n\n✅ Relatório salvo em: {output}")
    print(f"\n📖 Visualize: cat {output}")

if __name__ == "__main__":
    main()
