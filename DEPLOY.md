# 🚀 Guia de Deployment - Streamlit Cloud

## ⚠️ ERRO ENCONTRADO E CORRIGIDO

Ocorreu um erro durante o primeiro deployment:
```
E: Package 'chromium-browser' has no installation candidate
```

✅ **Solução implementada:** Veja [STREAMLIT_CLOUD_FIX.md](STREAMLIT_CLOUD_FIX.md) para detalhes

---

## ✅ Solução: Atualizar e Redeploy

### O que foi feito:
1. **Simplificado `packages.txt`** de 55 para 6 pacotes essenciais
2. **Melhorado `app.py`** para auto-detectar Chromium
3. **Adicionado fallback** para webdriver-manager

### Passos para Deploy:

#### 1️⃣ **Verificar arquivos localmente**
```bash
# Confirme que estes arquivos foram atualizados:
- packages.txt        ← Agora com apenas 6 pacotes
- app.py             ← Função criar_driver() otimizada
```

**Novo `packages.txt` deve conter:**
```
chromium
chromium-driver
xvfb
libxi6
libgconf-2-4
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
- Não deve haver erros de "not found"

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
xvfb
libxi6
libgconf-2-4
fonts-liberation
```

### `.streamlit/config.toml` ✅
Configuração do tema e comportamento

---

## 🔍 Se Não Funcionar

### Erro: "Package chromium-browser has no installation candidate"
**Solução:**
- Verifique que `packages.txt` tem exatamente os 6 pacotes acima
- Remova espaços em branco extras
- Clique em "Redeploy" (não reload)

### Erro: "Chrome not found"
**Solução:**
- Rode `python diagnostico.py` localmente
- Se funcionar localmente, o problema é só no deployment
- Tente "Reboot" depois "Redeploy"

### Timeout ou Erro de Conexão
**Solução:**
- Aumentar `TIMEOUT_PADRAO` e `TIMEOUT_ENVIO`
- Verificar URL do formulário
- Testar com formulário simples primeiro

---

## ✅ Checklist Final

- [ ] Confirmou que `packages.txt` tem 6 linhas
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

**Status:** ✅ Corrigido e pronto para deployment
**Data:** 14 de maio de 2026



