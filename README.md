# Automação de Formulários Google Forms

Duas versões disponíveis:

## 📄 main.py (Versão Original)
A versão original e funcional. **Use esta em produção.**

## ✨ main-melhor.py (Versão Melhorada)
Versão com melhorias de segurança, robustez e manutenibilidade. **Use para testes antes de considerar a produção.**

---

## 🚀 Como Usar main-melhor.py

### 1. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 2. Configurar Variáveis de Ambiente
```bash
# Copie o arquivo de exemplo
copy .env.example .env

# Edite .env com seus dados:
# NOME_FUNCIONARIO=Seu Nome
# ID_FUNCIONARIO=12345
# TELEFONE=85988449973
```

### 3. Executar
```bash
python main-melhor.py
```

Cole a URL do Google Forms quando solicitado.

---

## 📋 Melhorias Implementadas

### Segurança 🔒
- ✅ Dados sensíveis movidos para `.env` (não commit no Git)
- ✅ Validação de URL do formulário
- ✅ Sem exposição de informações pessoais no código-fonte

### Robustez 💪
- ✅ Logging detalhado em arquivo (`automacao_forms.log`) e console
- ✅ Tratamento de exceções específicas (não genérico)
- ✅ Retry automático com backoff para falhas temporárias
- ✅ Múltiplas estratégias para localizar elementos
- ✅ Validação de dados carregados do `.env`

### Performance 🚀
- ✅ Mais uso de `WebDriverWait` em vez de `time.sleep()` fixo
- ✅ TimeOuts dinâmicos e configuráveis
- ✅ Melhor utilização de recursos

### Manutenibilidade 📚
- ✅ Type hints em todas as funções
- ✅ Docstrings descritivas
- ✅ Código mais legível e organizado
- ✅ Resumo final com taxa de sucesso
- ✅ Arquivo `requirements.txt`

### Debugabilidade 🔍
- ✅ Logs estruturados com timestamp
- ✅ Rastreamento de tentativas e erros
- ✅ Arquivo de log persistente para auditoria

---

## 📊 Exemplo de Log

```
2026-05-13 14:30:45,123 - INFO - ============================================================
2026-05-13 14:30:45,124 - INFO - 🚀 INICIANDO AUTOMAÇÃO DE FORMULÁRIOS
2026-05-13 14:30:45,124 - INFO - ============================================================
2026-05-13 14:30:52,456 - INFO - 🌐 URL validada: https://docs.google.com/forms/d/...
2026-05-13 14:30:52,789 - INFO - 🔍 Iniciando mapeamento de rotas disponíveis...
2026-05-13 14:31:12,345 - INFO - ✅ Rota 1: Cambeba
2026-05-13 14:31:12,456 - INFO - ✅ Rota 2: Guararapes
...
2026-05-13 14:35:23,789 - INFO - ============================================================
2026-05-13 14:35:23,790 - INFO - 📈 RESUMO FINAL
2026-05-13 14:35:23,791 - INFO - ============================================================
2026-05-13 14:35:23,791 - INFO - ✅ Sucessos: 25
2026-05-13 14:35:23,792 - INFO - ❌ Falhas: 2
2026-05-13 14:35:23,793 - INFO - 📊 Taxa de sucesso: 92.6%
```

---

## ⚙️ Configurações Ajustáveis

No arquivo `main-melhor.py`, você pode modificar:

```python
TIMEOUT_PADRAO = 15                 # Timeout para mapeamento
TIMEOUT_ENVIO = 20                  # Timeout para envio
INTERVALO_ENTRE_ENVIOS = 3          # Segundos entre formulários
MAX_TENTATIVAS = 2                  # Retry automático
INTERVALO_RETRY = 2                 # Segundos antes de retry
```

---

## 🔄 Comparação: main.py vs main-melhor.py

| Aspecto | main.py | main-melhor.py |
|---------|---------|----------------|
| Dados sensíveis | Hardcoded ❌ | `.env` ✅ |
| Logging | `print()` ⚠️ | Arquivo + console ✅ |
| Tratamento de erro | Genérico ❌ | Específico ✅ |
| Type hints | Não ❌ | Sim ✅ |
| Retry automático | Não ❌ | Sim ✅ |
| Múltiplas estratégias XPath | Não ❌ | Sim ✅ |
| Validação de URL | Não ❌ | Sim ✅ |
| Resumo final | Não ❌ | Sim ✅ |

---

## ⚠️ Notas Importantes

1. **Não commit do .env**: Adicione a `.gitignore` antes de fazer push
2. **ChromeDriver**: Baixado automaticamente via `webdriver-manager`
3. **Logs persistem**: Verifique `automacao_forms.log` para histórico completo
4. **Headless mode**: Descomente a linha em `criar_driver()` para execução sem interface visual

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'dotenv'"
```bash
pip install python-dotenv
```

### "Variáveis de ambiente não configuradas"
Crie um arquivo `.env` na raiz do projeto com os dados requeridos (veja `.env.example`)

### ChromeDriver incompatível
```bash
pip install --upgrade webdriver-manager
```

---

## 📞 Contato
Para problemas, verifique o log em `automacao_forms.log`
