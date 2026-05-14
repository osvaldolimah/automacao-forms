# ⚡ Guia Rápido - Corrigir Erro do Streamlit Cloud

## 🎯 O Problema
Erro: `E: Unable to locate package libgconf-2-4`

O `packages.txt` tem pacotes que não existem em versões modernas do Debian.

## ✅ A Solução (3 passos)

### 1️⃣ Fazer Commit
```bash
git add packages.txt
git commit -m "Fix: Remover pacotes obsoletos do packages.txt"
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

**`packages.txt`** (agora apenas 3 pacotes essenciais):
```
chromium
chromium-driver
fonts-liberation
```

**Por quê?**
- Outros pacotes não existem/são obsoletos no Debian atual
- Estes 3 são os únicos necessários e disponíveis
- Chromium já traz suas dependências

---

## ✨ Local Funciona?

```bash
python diagnostico.py
```

Resultado: ✅ **Ambiente parece estar OK!**

---

## ❓ Se não funcionar

### A. Verificar packages.txt
```bash
cat packages.txt
```

Deve ter EXATAMENTE:
```
chromium
chromium-driver
fonts-liberation
```

### B. Forçar redeploy
1. Clique em "Reboot" 
2. Depois clique em "Redeploy"

### C. Verificar logs
- Procure por "chromium" sendo instalado
- Não deve ter erros de "not found"

---

**Pronto! Faça o push e redeploy!** 🚀



