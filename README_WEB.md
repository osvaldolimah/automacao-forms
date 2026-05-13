# 🌐 Automação Forms - Web Interface + API

Executa a automação de formulários Google **direto do seu celular** via interface web hospedada no GitHub Pages!

---

## ✨ Características

- 📱 **Interface Web Responsiva** - Funciona perfeitamente em celular
- ☁️ **Hospedagem Gratuita** - GitHub Pages (sem custo)
- 🖥️ **API em sua VPS** - Usa sua infraestrutura existente
- 🔄 **Priorização de Bairros** - Envia na ordem de sua preferência
- 📊 **Resultado em Tempo Real** - Vê sucesso/falha de cada rota
- 🚀 **24/7** - Disponível sempre que quiser

---

## 🚀 Quick Start

### Fase 1: Preparar a VPS (DigitalOcean)

1. Acesse sua VPS via SSH:
   ```bash
   ssh root@SEU_IP
   ```

2. Clone ou copie os arquivos:
   - `api_automacao.py`
   - `.env` (com suas credenciais)
   - `requirements-api.txt`

3. Instale dependências:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements-api.txt
   apt install -y chromium-browser  # ou google-chrome
   ```

4. Inicie a API:
   ```bash
   python3 api_automacao.py &
   ```

   A API estará em: `http://SEU_IP:5000`

### Fase 2: Hospedar no GitHub Pages

1. Crie um repositório no GitHub (ex: `automacao-forms`)
2. Copie `index.html` para o repositório
3. Ative GitHub Pages nas configurações
4. Sua interface estará em: `https://SEU_USUARIO.github.io/automacao-forms/`

### Fase 3: Usar no Celular

1. Abra no navegador: `https://SEU_USUARIO.github.io/automacao-forms/`
2. Clique em "Clique aqui para configurar" e digite: `http://SEU_IP:5000`
3. Cole a URL do formulário Google
4. Clique em **Executar Automação**

---

## 📁 Arquivos

| Arquivo | Descrição | Local |
|---------|-----------|-------|
| `api_automacao.py` | API Flask que executa a automação | VPS |
| `index.html` | Interface web | GitHub Pages |
| `.env` | Credenciais do formulário | VPS (seguro) |
| `requirements-api.txt` | Dependências Python | VPS |
| `GUIA_DEPLOY.md` | Instruções detalhadas de setup | Referência |

---

## 🔄 Fluxo de Funcionamento

```
CELULAR (Navegador)
   ↓
[GitHub Pages - index.html]
   ↓ HTTPS
[Sua VPS - api_automacao.py]
   ↓ Selenium
[Google Forms - Preenche e Envia]
   ↓
[Resultado - volta para o celular]
```

---

## 📡 Endpoints da API

### GET `/health`
Verifica se a API está rodando.

**Resposta:**
```json
{
  "status": "ok",
  "timestamp": "2026-05-13T10:30:00.000000"
}
```

### POST `/executar`
Executa a automação para uma URL de formulário.

**Requisição:**
```json
{
  "url": "https://forms.gle/..."
}
```

**Resposta (Sucesso):**
```json
{
  "status": "sucesso",
  "resumo": {
    "total_rotas": 9,
    "sucesso": 9,
    "falha": 0,
    "percentual_sucesso": 100.0
  },
  "rotas": [
    {
      "rota": "Fortaleza - Parque Iracema - A-01",
      "status": "sucesso"
    },
    {
      "rota": "Fortaleza - Cajazeiras - B-15",
      "status": "sucesso"
    }
  ],
  "timestamp": "2026-05-13T10:35:00.000000"
}
```

---

## 🎨 Interface Web

### Recursos

- 🔗 Campo para colar URL do formulário
- ⚙️ Configuração de endereço VPS (salvo no navegador)
- 📊 Resumo com: total, sucessos, falhas, percentual
- 📋 Lista detalhada de cada rota processada
- ⏳ Indicador de carregamento durante execução
- 📱 Design responsivo (funciona em qualquer celular)

### Screenshot (Descrição)

```
┌─────────────────────────────────────────┐
│  🚀 Automação Forms                     │
│  Execute seus formulários do celular    │
├─────────────────────────────────────────┤
│  ⚙️ Configuração                         │
│  [http://seu-ip:5000]                   │
├─────────────────────────────────────────┤
│  URL do Formulário Google               │
│  [Cole a URL aqui...]                   │
│                                          │
│  [Executar Automação] [Limpar]           │
├─────────────────────────────────────────┤
│  ✅ Sucesso                              │
│                                          │
│  Total de Rotas: 9                       │
│  ✅ Enviadas com Sucesso: 9              │
│  ❌ Falhas: 0                            │
│  Taxa de Sucesso: 100.0%                │
│                                          │
│  Detalhes das Rotas:                     │
│  ✅ 1. Parque Iracema - OK               │
│  ✅ 2. Cajazeiras - OK                   │
│  ...                                     │
└─────────────────────────────────────────┘
```

---

## 🔐 Segurança

### Credenciais

Suas credenciais (.env) ficam **apenas na VPS**, nunca são enviadas para o navegador ou GitHub.

### API Access

A API aceita requisições de qualquer origem (CORS habilitado para GitHub Pages). 

**Para produção, considere adicionar autenticação:**
```python
# Exemplo: adicionar API Key
VALID_API_KEYS = ['sua-chave-secreta']

@app.before_request
def verify_api_key():
    if request.method != 'OPTIONS':
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key not in VALID_API_KEYS:
            return jsonify({'error': 'Unauthorized'}), 401
```

---

## 🛠️ Troubleshooting

### "Erro de conexão"
- Verifique se a VPS está rodando: `ps aux | grep api_automacao`
- Verifique a porta: `netstat -tuln | grep 5000`
- Verifique o firewall da VPS

### "Nenhuma rota compatível"
- O formulário contém os bairros? Verifique em `MEUS_BAIRROS`
- Os nomes dos bairros estão corretos (acentuação)?

### "Formulário não é preenchido"
- Chrome está instalado na VPS? `which chromium-browser`
- Verifique logs: `tail -f ~/automacao_forms/api.log`

---

## 📚 Documentação Completa

Veja [GUIA_DEPLOY.md](GUIA_DEPLOY.md) para instruções passo a passo de setup.

---

## 💡 Exemplos de Uso

### Caso 1: Usar via GitHub Pages (Recomendado)

1. Hospeda em: `https://seu-usuario.github.io/automacao-forms/`
2. Acessa pelo celular anytime, anywhere
3. Sem dependências locais

### Caso 2: Usar em PC Local

1. Abra `index.html` no navegador
2. Configure URL VPS: `http://localhost:5000`
3. Teste a integração antes de hospedar

---

## 🚀 Próximos Passos Opcionais

- [ ] Adicionar autenticação por API Key
- [ ] Implementar agendamento (cron jobs)
- [ ] Adicionar banco de dados (histórico)
- [ ] Dashboard com estatísticas
- [ ] Notificações por email/Telegram
- [ ] App nativa (React Native)

---

**Dúvidas? Veja [GUIA_DEPLOY.md](GUIA_DEPLOY.md) ou verifique os logs da VPS.**

Aproveite! 🎉
