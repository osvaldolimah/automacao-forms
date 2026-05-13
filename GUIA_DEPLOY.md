# 🚀 Guia de Deploy - Automação Forms com Web Interface

## 📋 Visão Geral

Este guia mostra como:
1. **VPS DigitalOcean**: Rodar a API Flask que executa a automação
2. **GitHub Pages**: Hospedar a página web (interface do usuário)
3. **Celular**: Acessar via navegador para executar a automação

---

## 📦 Arquivos Necessários

- `api_automacao.py` - API Flask (roda na VPS)
- `index.html` - Interface web (hospedada no GitHub Pages)
- `.env` - Credenciais (sua VPS, local seguro)
- `requirements.txt` - Dependências Python

---

## 🖥️ PARTE 1: CONFIGURAR NA VPS (DigitalOcean)

### Passo 1: Conectar na VPS

```bash
# Via SSH (substitua SEU_IP pelo IP da sua VPS)
ssh root@SEU_IP
```

### Passo 2: Criar Pasta do Projeto

```bash
mkdir -p ~/automacao_forms
cd ~/automacao_forms
```

### Passo 3: Copiar Arquivos

Você precisa enviar para a VPS:
- `api_automacao.py`
- `.env` (com suas credenciais)
- `requirements.txt`

**Opção A: Via SCP (recomendado)**
```bash
# No seu PC, execute (fora da VPS):
scp api_automacao.py root@SEU_IP:~/automacao_forms/
scp .env root@SEU_IP:~/automacao_forms/
scp requirements.txt root@SEU_IP:~/automacao_forms/
```

**Opção B: Copiar manualmente**
1. Abra a VPS
2. Crie os arquivos:
   ```bash
   nano ~/automacao_forms/api_automacao.py
   # Cole o conteúdo do arquivo, Ctrl+O para salvar, Ctrl+X para sair
   ```

### Passo 4: Criar Arquivo .env na VPS

```bash
nano ~/automacao_forms/.env
```

Cole (com seus dados):
```
NOME_FUNCIONARIO=Francisco Osvaldo Lima Holanda
ID_FUNCIONARIO=2445201
TELEFONE=85988449973
```

Salve: `Ctrl+O`, `Enter`, `Ctrl+X`

### Passo 5: Instalar Dependências

```bash
# Instalar Python (se não tiver)
apt update
apt install -y python3 python3-pip python3-venv

# Criar ambiente virtual
cd ~/automacao_forms
python3 -m venv venv

# Ativar ambiente
source venv/bin/activate

# Instalar pacotes
pip install -r requirements.txt
```

**Se não tiver requirements.txt, instale diretamente:**
```bash
pip install flask flask-cors selenium webdriver-manager python-dotenv
```

### Passo 6: Instalar ChromeDriver (para Selenium)

A boa notícia: `webdriver-manager` faz isso automaticamente!

Mas você precisa de Chrome/Chromium na VPS:

```bash
# Instalar Chromium (mais leve que Chrome)
apt install -y chromium-browser

# Ou instalar Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
dpkg -i google-chrome-stable_current_amd64.deb
```

### Passo 7: Testar a API Localmente (na VPS)

```bash
cd ~/automacao_forms
source venv/bin/activate
python3 api_automacao.py
```

Você deve ver:
```
 * Serving Flask app 'app'
 * Debug mode: off
 * Running on http://0.0.0.0:5000
```

**Teste** (em outro terminal da VPS):
```bash
curl http://localhost:5000/health
```

Deve retornar JSON com status "ok".

Pressione `Ctrl+C` para parar a API.

### Passo 8: Rodar a API em Background (Permanente)

Você quer que a API rode 24/7. Use `nohup`:

```bash
cd ~/automacao_forms
source venv/bin/activate
nohup python3 api_automacao.py > api.log 2>&1 &
```

**Verificar se está rodando:**
```bash
ps aux | grep api_automacao.py
```

**Ver logs:**
```bash
tail -f ~/automacao_forms/api.log
```

**Parar a API:**
```bash
pkill -f api_automacao.py
```

### Passo 9: (Opcional) Usar Supervisor para Auto-Restart

Se a API cair, reinicia automaticamente:

```bash
# Instalar supervisor
apt install -y supervisor

# Criar arquivo de configuração
nano /etc/supervisor/conf.d/automacao_forms.conf
```

Cole:
```ini
[program:automacao_forms]
directory=/root/automacao_forms
command=/root/automacao_forms/venv/bin/python3 api_automacao.py
autostart=true
autorestart=true
stderr_logfile=/var/log/automacao_forms.err.log
stdout_logfile=/var/log/automacao_forms.out.log
```

Ative:
```bash
supervisorctl reread
supervisorctl update
supervisorctl start automacao_forms
```

---

## 🌐 PARTE 2: HOSPEDAR NO GITHUB PAGES

### Passo 1: Criar Repositório no GitHub

1. Acesse [github.com](https://github.com)
2. Clique em **New repository**
3. Nome: `automacao-forms` (ou outro nome)
4. Defina como **Public** (necessário para GitHub Pages)
5. Clique **Create repository**

### Passo 2: Clonar o Repositório

```bash
git clone https://github.com/SEU_USUARIO/automacao-forms.git
cd automacao-forms
```

### Passo 3: Copiar o arquivo index.html

```bash
# Copie seu index.html para a pasta do repositório
cp /caminho/para/seu/index.html .
```

### Passo 4: Fazer Commit e Push

```bash
git add index.html
git commit -m "Adiciona interface da automação"
git push origin main
```

### Passo 5: Ativar GitHub Pages

1. Vá para **Settings** do repositório
2. Procure por **Pages** no menu esquerdo
3. Em "Source", selecione **main** (ou branch principal)
4. Clique **Save**

Espere alguns minutos. Você verá:
```
Your site is published at https://SEU_USUARIO.github.io/automacao-forms/
```

---

## 📱 PARTE 3: USAR NO CELULAR

### Acessar a Página

1. Abra o navegador do seu celular
2. Digite: `https://SEU_USUARIO.github.io/automacao-forms/`
3. Você verá a interface

### Configurar a URL da VPS

1. Na página, clique em **"Clique aqui para configurar"** (onde está o endereço da VPS)
2. Digite o endereço da sua VPS: `http://SEU_IP:5000`
   - Se tiver domínio: `http://seu-dominio.com:5000`
3. Clique **OK** (fica salvo no celular)

### Executar a Automação

1. Cole a URL do formulário Google
2. Clique **Executar Automação**
3. Aguarde (pode levar alguns minutos)
4. Veja o resultado (rotas, sucessos, falhas)

---

## 🔧 TROUBLESHOOTING

### Problema: "Erro de conexão"

**Causa**: VPS não está acessível

**Solução**:
```bash
# 1. Verificar se a API está rodando na VPS
ssh root@SEU_IP
ps aux | grep api_automacao.py

# 2. Verificar se porta 5000 está aberta
netstat -tuln | grep 5000

# 3. Se não está rodando, inicie:
cd ~/automacao_forms
source venv/bin/activate
python3 api_automacao.py &
```

### Problema: "URL inválida"

**Causa**: URL do formulário incorreta

**Solução**:
- Use: `https://forms.gle/...` (atalho)
- Ou: `https://docs.google.com/forms/d/...` (URL completa)

### Problema: "Nenhuma rota compatível encontrada"

**Causa**: Formulário não tem rotas que match com MEUS_BAIRROS

**Solução**:
- Verifique se o formulário contém os bairros corretos
- Verifique a lista `MEUS_BAIRROS` em `api_automacao.py`

### Problema: Formulário não é preenchido

**Causa**: ChromeDriver não está funcionando

**Solução** (na VPS):
```bash
# Verificar logs
tail -f ~/automacao_forms/api.log

# Reinstalar Chromium
apt remove -y chromium-browser
apt install -y chromium-browser
```

---

## 📊 MONITORAMENTO

### Ver Status da API (na VPS)

```bash
# Logs em tempo real
tail -f ~/automacao_forms/api.log

# Ou (se usar supervisor)
tail -f /var/log/automacao_forms.out.log
```

### Testar API pelo Navegador (PC ou Celular)

```
http://SEU_IP:5000/health
```

Deve retornar:
```json
{"status": "ok", "timestamp": "2026-05-13T..."}
```

---

## 🔐 SEGURANÇA

### ⚠️ NÃO FAÇA:
- ❌ Não coloque `.env` no GitHub (credenciais expostas!)
- ❌ Não deixe a API pública sem autenticação
- ❌ Não use `debug=True` em produção

### ✅ RECOMENDAÇÕES:
- ✅ Adicione autenticação (API key simples)
- ✅ Use HTTPS (Let's Encrypt na VPS)
- ✅ Monitore logs regularmente
- ✅ Faça backup dos dados

---

## 📝 RESUMO DO FLUXO

```
SEU CELULAR
   ↓
[GitHub Pages - index.html]
   ↓ (HTTPS)
[SUA VPS - api_automacao.py:5000]
   ↓ (Selenium)
[Google Forms]
```

---

## 🆘 PRECISA DE AJUDA?

1. **Verifique os logs** (VPS):
   ```bash
   tail -f ~/automacao_forms/api.log
   ```

2. **Teste a API localmente**:
   ```bash
   curl -X POST http://localhost:5000/executar \
     -H "Content-Type: application/json" \
     -d '{"url": "https://forms.gle/..."}'
   ```

3. **Verifique a conectividade**:
   ```bash
   curl http://SEU_IP:5000/health
   ```

---

**Pronto! 🎉 Agora você pode executar a automação do seu celular a qualquer hora!**
