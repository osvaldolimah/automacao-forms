# ⚡ Guia Rápido - Corrigir Error do Streamlit Cloud

## 🎯 O Problema
O deployment falhou com erro de pacotes não encontrados.

## ✅ A Solução (3 passos)

### 1️⃣ Fazer Commit
```bash
git add .
git commit -m "Fix: Simplificar packages.txt para Streamlit Cloud"
git push origin main
```

### 2️⃣ Redeploy
1. Acesse: https://share.streamlit.io
2. Clique em **"Redeploy"** (não reload!)
3. Aguarde "App is live"

### 3️⃣ Testar
- Acesse sua URL do Streamlit
- Insira URL do formulário
- Clique "Mapear Rotas"

---

## 📝 O Que Mudou

**`packages.txt`** (agora 6 linhas apenas):
```
chromium
chromium-driver
xvfb
libxi6
libgconf-2-4
fonts-liberation
```

**`app.py`** (melhorado para auto-detectar Chrome):
- ✅ Agora funciona com Streamlit Cloud
- ✅ Mantém compatibilidade local

---

## ❓ Se não funcionar

### A. Verificar packages.txt
```bash
# Deve ter EXATAMENTE essas 6 linhas
cat packages.txt
```

### B. Forçar redeploy
1. Clique em "Reboot" nas configurações
2. Depois clique em "Redeploy"

### C. Verificar logs
- Clique em "Logs" durante deployment
- Procure por "chromium" ou erros

---

## ✨ Local Funciona?

```bash
python diagnostico.py
```

Se mostrar ✅ verde, está OK!

---

**Pronto! Agora faça o push e redeploy!** 🚀

