# 🚀 Guia de Deployment - Streamlit Cloud

## ✅ Status Atual

A aplicação já está funcionando no Streamlit Cloud.

### O que foi feito
1. `packages.txt` foi reduzido para os pacotes essenciais
2. `app.py` foi ajustado para funcionar em ambiente headless
3. O fluxo de mapeamento e envio foi validado no Cloud

### Passos para Deploy:

#### 1️⃣ **Verificar arquivos localmente**
```bash
# Confirme que estes arquivos foram atualizados:
- packages.txt        ← Agora com apenas 3 pacotes
- app.py             ← Função criar_driver() otimizada e estável
```

**`packages.txt` deve conter:**
```
chromium
chromium-driver
fonts-liberation
```

#### 2️⃣ **Fazer commit e push**
```bash
git add packages.txt app.py
git commit -m "Fix: Simplificar packages.txt para Streamlit Cloud"
git push origin main
```

#### 3️⃣ **Redeploy no Streamlit Cloud** (IMPORTANTE)
- Acesse [https://share.streamlit.io](https://share.streamlit.io)
- Clique em "Redeploy" (NÃO reload!)
- Aguarde até ver "App is live"

**Logs esperados:**
```
[12:11:14] 📦 Processing dependencies...
[12:11:14] 📦 Apt dependencies were installed from packages.txt
[12:11:XX] 🚀 App is live!
```

#### 4️⃣ **Verificar Logs**
- Durante deployment, clique em "Logs"
- Procure por "chromium" sendo instalado
- Se aparecer erro, confirme se é um redeploy novo e não um reload

---

## 📋 Arquivos Necessários

### `requirements.txt` ✅
```
streamlit>=1.32.0
selenium>=4.18.0
webdriver-manager>=4.0.1
```

### `packages.txt` ✅ (SIMPLIFICADO)
```
chromium
chromium-driver
fonts-liberation
```

### `.streamlit/config.toml` ✅
Configuração do tema e comportamento

---

## 🔍 Se Não Funcionar

### Erro: "Chrome not found"
**Solução:**
- Verifique que `packages.txt` tem exatamente 3 pacotes
- Faça um novo "Redeploy" (não apenas reload)
- Aguarde o deployment completar

### Timeout ou Erro de Conexão
**Solução:**
- Aumentar `TIMEOUT_PADRAO` e `TIMEOUT_ENVIO`
- Verificar URL do formulário
- Testar com formulário simples primeiro

---

## ✅ Checklist Final

- [ ] Confirmou que `packages.txt` tem 3 linhas
- [ ] Confirmou que `app.py` foi atualizado
- [ ] Rodou `python diagnostico.py` com sucesso
- [ ] Fez `git push` para GitHub
- [ ] Clicou em "Redeploy" (NÃO reload)
- [ ] Aguardou até "App is live"
- [ ] Verificou os logs
- [ ] Testou a URL do app
- [ ] Confirmou "Mapear Rotas" funciona

---

## 📚 Referências

- [Streamlit Cloud Docs](https://docs.streamlit.io/streamlit-community-cloud)
- [Streamlit Cloud System Dependencies](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/app-dependencies)
- [STREAMLIT_CLOUD_FIX.md](STREAMLIT_CLOUD_FIX.md) - Detalhes técnicos do fix

---

**Status:** ✅ Aplicação estável e funcionando no Cloud
**Data:** 14 de maio de 2026



