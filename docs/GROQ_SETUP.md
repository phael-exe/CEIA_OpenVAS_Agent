# 🚀 Guia Rápido: Usando Groq (Modelos Opensource GRATUITOS)

## Por que Groq?

- ✅ **100% Gratuito** - Sem necessidade de cartão de crédito
- ⚡ **Ultra-rápido** - Inferência otimizada para LLMs
- 🔓 **Modelos Opensource** - Llama 3.1, Mixtral, Gemma
- 🎯 **Alta qualidade** - Performance comparável ao GPT-4

## Passo 1: Criar Conta

1. Acesse: https://console.groq.com
2. Clique em **Sign Up** (pode usar conta Google/GitHub)
3. Confirme seu email

## Passo 2: Gerar API Key

1. No dashboard, vá em **API Keys** (menu lateral)
2. Clique em **Create API Key**
3. Dê um nome (ex: "OpenVAS Agent")
4. Copie a chave que começa com `gsk_...`

⚠️ **IMPORTANTE**: Copie a chave agora! Ela só é mostrada uma vez.

## Passo 3: Configurar no .env

Abra o arquivo `.env` e adicione:

```bash
# Groq Configuration (GRATUITO!)
GROQ_API_KEY = 'gsk_sua_chave_aqui'
GROQ_MODEL_ID = 'llama-3.1-70b-versatile'
LLM_PROVIDER = 'groq'
```

## Modelos Disponíveis

### Llama 3.1 (Meta) - Recomendado
- **llama-3.1-70b-versatile** ⭐ - Melhor balanço qualidade/velocidade
- **llama-3.1-8b-instant** - Mais rápido, bom para tarefas simples
- **llama-3.2-90b-text-preview** - Mais poderoso

### Mixtral (Mistral AI)
- **mixtral-8x7b-32768** - Grande janela de contexto (32k tokens)

### Gemma (Google)
- **gemma2-9b-it** - Compacto e eficiente

## Comparação de Performance

| Modelo | Velocidade | Qualidade | Contexto | Recomendado Para |
|--------|-----------|-----------|----------|------------------|
| llama-3.1-70b-versatile | ⚡⚡⚡ | ⭐⭐⭐⭐ | 128k | Análise geral ✅ |
| llama-3.1-8b-instant | ⚡⚡⚡⚡⚡ | ⭐⭐⭐ | 128k | Respostas rápidas |
| mixtral-8x7b-32768 | ⚡⚡⚡ | ⭐⭐⭐⭐ | 32k | CSVs grandes |
| llama-3.2-90b-preview | ⚡⚡ | ⭐⭐⭐⭐⭐ | 128k | Análise complexa |

## Limites da API Gratuita

- **Requests/minuto**: 30 RPM
- **Tokens/minuto**: 14,400 TPM
- **Requests/dia**: 14,400 RPD

💡 **Suficiente para**: Analisar centenas de CSVs por dia!

## Testando a Configuração

```bash
# Teste simples
python test_csv_analyzer.py

# Ou via Streamlit
streamlit run streamlit_app.py
```

## Troubleshooting

### ❌ Erro: "Invalid API Key"
- Verifique se copiou a chave completa (começa com `gsk_`)
- Certifique-se de que está entre aspas no `.env`
- Tente regenerar a chave no console Groq

### ❌ Erro: "Rate limit exceeded"
- Aguarde 1 minuto e tente novamente
- Considere processar CSVs em lotes menores

### ❌ Erro: "Module not found: langchain_groq"
```bash
pip install langchain-groq
```

## Vantagens vs OpenAI

| Aspecto | Groq | OpenAI |
|---------|------|--------|
| Custo | 🆓 Grátis | 💰 Pago |
| Velocidade | ⚡ Mais rápido | ⚡ Rápido |
| Qualidade | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Setup | ✅ Simples | ✅ Simples |
| Limites | 30 RPM | Por crédito |

## Dicas de Otimização

1. **Use llama-3.1-70b-versatile** para maioria dos casos
2. **Switch para 8b-instant** se precisar de velocidade máxima
3. **Processe múltiplos CSVs** - o limite de 30 RPM é generoso
4. **Cache resultados** - salve os relatórios para consulta posterior

## Links Úteis

- 📚 Documentação: https://console.groq.com/docs
- 🎮 Playground: https://console.groq.com/playground
- 💬 Discord: https://discord.gg/groq
- 🐙 GitHub: https://github.com/groq

---

**Pronto! Agora você tem acesso a IA gratuita e potente para análise de vulnerabilidades! 🎉**
