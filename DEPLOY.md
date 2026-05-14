# 🚀 Guia de Deployment - Streamlit Cloud

## Problema: Automação não funciona no Streamlit Cloud

O Streamlit Cloud não possui Chrome/Chromium pré-instalado por padrão. Para que a automação com Selenium funcione, é necessário instalar essas dependências do sistema.

---

## ✅ Solução: Atualizar `packages.txt`

### O que foi feito:
1. **Atualizado `packages.txt`** com todas as dependências necessárias do Debian
2. **Melhorado `app.py`** para detectar automaticamente o Chromium no Streamlit Cloud
3. **Adicionado fallback** para ambientes locais com `webdriver-manager`

### Passos para Deploy:

#### 1️⃣ **Verificar arquivos localmente**
```bash
# Confirme que estes arquivos foram atualizados:
- packages.txt        ← Contém dependências do Debian
- requirements.txt    ← Contém pacotes Python
- app.py             ← Contém lógica de detecção de Chrome
- .streamlit/config.toml
```

#### 2️⃣ **Fazer commit e push**
```bash
git add packages.txt requirements.txt app.py
git commit -m "fix: Adicionar suporte para Chromium no Streamlit Cloud"
git push origin main
```

#### 3️⃣ **Redeployar no Streamlit Cloud**
- Acesse [https://share.streamlit.io](https://share.streamlit.io)
- Clique em "Redeploy" para a sua aplicação
- **NÃO** cancele o deployment até ele terminar
- Acompanhe os logs para ver se Chromium está sendo instalado

#### 4️⃣ **Verificar Logs**
Durante o deployment, você verá logs como:
```
[installer] Installing packages...
[installer] chromium-browser
[installer] fonts-liberation
[installer] libappindicator3-1
...
```

---

## 📋 Arquivos Necessários

### `requirements.txt`
```
streamlit>=1.32.0
selenium>=4.18.0
webdriver-manager>=4.0.1
```

### `packages.txt`
Contém 50+ pacotes de dependência do Debian (veja arquivo atual)

### `.streamlit/config.toml`
Configuração do tema e comportamento do Streamlit

---

## 🔍 Diagnosticar Problemas

### Se ainda não funcionar:

**1. Verifique os logs do deployment:**
- Procure por erros como "chromium-browser not found"
- Se houver erro de espaço, talvez algum pacote não tenha sido instalado

**2. Teste localmente primeiro:**
```bash
# Ativar ambiente virtual
.\.venv\Scripts\Activate.ps1

# Testar app
streamlit run app.py
```

**3. Se local funciona mas cloud não:**
- Verifique se `packages.txt` tem exatamente os pacotes certos
- Tente remover espaços em branco extras no arquivo
- Redeploy novamente

---

## 📚 Referências

- [Streamlit Cloud Docs - System Dependencies](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/app-dependencies)
- [Selenium Python Docs](https://selenium-python.readthedocs.io/)
- [Chrome/Chromium no Debian](https://wiki.debian.org/Chromium)

---

## ⚠️ Possíveis Alternativas (se ainda não funcionar)

Se o deployment no Streamlit Cloud continuar falhando, existem alternativas:

### Opção A: Usar Heroku (deprecated - não recomendado)
### Opção B: Deploy em seu próprio servidor (VPS)
### Opção C: Usar serviço como Railway, Render, ou PythonAnywhere
### Opção D: Reescrever com API (sem Selenium, mas sem automação de cliques)

---

**Última atualização:** 14 de maio de 2026

