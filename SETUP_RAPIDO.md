# 🚀 SETUP AUTOMÁTICO VPS - GUIA PASSO A PASSO

## 📋 Resumo

Este guia automatiza TUDO na VPS em 3 etapas:

```
PC (seu notebook)
   ↓
[Copiar arquivos para VPS]
   ↓
VPS (159.203.134.102)
   ↓
[Executar setup.sh - instala tudo]
   ↓
✅ API rodando!
```

---

## ⚡ RÁPIDO (5 minutos)

### Opção 1: PowerShell (Recomendado para Windows)

```powershell
# 1. Abra PowerShell como Administrator
# 2. Navegue para a pasta
cd c:\Users\zoval\OneDrive\Documentos\automacao_forms

# 3. Execute o deploy
powershell -ExecutionPolicy Bypass -File deploy.ps1

# Ele vai copiar os arquivos automaticamente
```

### Opção 2: Git Bash / WSL

```bash
# 1. Abra Git Bash ou WSL Terminal
# 2. Navegue para a pasta
cd /c/Users/zoval/OneDrive/Documentos/automacao_forms

# 3. Execute
bash deploy.sh
```

### Opção 3: Terminal (Se tiver SSH configurado)

```bash
# No seu PC, de qualquer pasta:
scp c:\Users\zoval\OneDrive\Documentos\automacao_forms\api_automacao.py root@159.203.134.102:/root/automacao_forms/
scp c:\Users\zoval\OneDrive\Documentos\automacao_forms\requirements-api.txt root@159.203.134.102:/root/automacao_forms/
scp c:\Users\zoval\OneDrive\Documentos\automacao_forms\setup.sh root@159.203.134.102:/root/automacao_forms/
```

---

## 🖥️ EXECUTAR NA VPS

Depois de copiar os arquivos:

### 1. Conectar na VPS

```bash
ssh root@159.203.134.102
```

Você vai ver:
```
root@vps:~#
```

### 2. Executar Setup

```bash
cd /root/automacao_forms
bash setup.sh
```

**Pode demorar 2-3 minutos** enquanto instala tudo.

Você verá:
```
[1/7] 📦 Atualizando sistema...
[2/7] 📦 Instalando dependências...
[3/7] 📁 Criando estrutura...
[4/7] 🐍 Instalando Python...
[5/7] 🔐 Criando .env...
[6/7] 📥 Criando API...
[7/7] ✅ Verificando...
```

### 3. Próximos Passos (conforme mensagem ao final)

```bash
# 1️⃣ Ativar ambiente (se não estiver)
source venv/bin/activate

# 2️⃣ Iniciar a API em background
nohup python3 api_automacao.py > api.log 2>&1 &

# 3️⃣ Verificar se está rodando
curl http://localhost:5000/health
```

Você deve ver:
```json
{"status": "ok", "timestamp": "2026-05-13T..."}
```

---

## ✅ VERIFICAR SE ESTÁ FUNCIONANDO

### Teste 1: Local (na VPS)

```bash
curl http://localhost:5000/health
```

Resposta esperada:
```json
{"status": "ok"}
```

### Teste 2: De outro PC

```bash
# Do seu PC, em outro terminal:
curl http://159.203.134.102:5000/health
```

Se funcionar, a API está 100% acessível!

### Teste 3: Executar Automação

```bash
curl -X POST http://159.203.134.102:5000/executar \
  -H "Content-Type: application/json" \
  -d '{"url": "https://forms.gle/XXXX"}'
```

---

## 🔍 MONITORAR A EXECUÇÃO

### Ver logs em tempo real

```bash
tail -f ~/automacao_forms/api.log
```

### Ver se o processo está rodando

```bash
ps aux | grep api_automacao.py
```

Vai retornar algo como:
```
root 12345 0.5 2.1 123456 78901 ? Sl 10:30 0:05 /root/automacao_forms/venv/bin/python3 api_automacao.py
```

### Parar a API (se necessário)

```bash
pkill -f api_automacao.py
```

### Reiniciar

```bash
nohup python3 api_automacao.py > api.log 2>&1 &
```

---

## 🌐 USAR NA INTERFACE WEB

### 1. Você tem GitHub Pages?

Se não, veja [GUIA_DEPLOY.md](GUIA_DEPLOY.md)

### 2. Acessar no Celular

```
https://seu-usuario.github.io/automacao-forms/
```

### 3. Configurar IP da VPS

Na página web, clique em "Clique aqui para configurar" e coloque:

```
http://159.203.134.102:5000
```

### 4. Pronto!

Cole a URL do formulário e clique em **Executar Automação**.

---

## 🆘 TROUBLESHOOTING

### Problema: "Connection refused"

```bash
# Verificar se está rodando
ps aux | grep api_automacao.py

# Se não estiver, iniciar
nohup python3 api_automacao.py > api.log 2>&1 &
```

### Problema: "Command not found" (scp)

Você precisa de SSH instalado. No Windows:
- Use PowerShell 7+ (tem SSH nativo)
- Ou instale Git Bash / WSL2

### Problema: "Permission denied"

Adicione permissão de execução:
```bash
chmod +x setup.sh
bash setup.sh
```

### Problema: Chrome não inicia

```bash
# Verificar instalação
which chromium-browser

# Reinstalar se necessário
apt remove -y chromium-browser
apt install -y chromium-browser
```

### Problema: Python não encontrado

```bash
# Verificar versão
python3 --version

# Deve ser 3.10+
```

---

## 📊 RESUMO DO QUE FOI INSTALADO

| Component | Versão | Função |
|-----------|--------|--------|
| Python | 3.10.12 | Linguagem |
| Flask | 2.3.3 | API Web |
| Selenium | 4.15.2 | Automação |
| Chrome | Latest | Browser |
| webdriver-manager | 4.0.1 | Gerencia ChromeDriver |
| python-dotenv | 1.0.0 | Carrega .env |

---

## 🎯 PRÓXIMO PASSO

Depois que a API estiver rodando, siga para:

1. **[GUIA_DEPLOY.md](GUIA_DEPLOY.md)** - Configurar GitHub Pages
2. **README_WEB.md** - Entender a interface web

---

## 💡 DICAS

- **Manter API sempre rodando**: Use `supervisor` (veja GUIA_DEPLOY.md)
- **Usar domínio em vez de IP**: Configure DNS na VPS (mais profissional)
- **HTTPS**: Instale Let's Encrypt na VPS (segurança)
- **Backups**: Faça backup de `automacao_forms/` regularmente

---

**Tudo pronto? Comece pelo Step 1! 🚀**
