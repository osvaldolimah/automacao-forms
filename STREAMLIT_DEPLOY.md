# 🚀 DEPLOY NO STREAMLIT CLOUD

## Passo 1: Preparar o repositório GitHub

```bash
# Certifique-se de que tem esses arquivos no seu repositório:
app.py                    # Aplicação Streamlit
requirements.txt          # Dependências
.streamlit/config.toml   # Configuração
.streamlit/secrets.toml  # (será criado no Streamlit Cloud)
.env                     # (local, não fazer commit)
```

## Passo 2: Fazer commit e push para GitHub

```bash
git add app.py requirements.txt .streamlit/
git commit -m "Add Streamlit app with Playwright"
git push origin main
```

## Passo 3: Deploy no Streamlit Cloud

1. Vá para https://share.streamlit.io
2. Clique em "New app"
3. Selecione seu repositório GitHub
4. Selecione o branch "main"
5. Define o caminho para o arquivo: `app.py`
6. Clique "Deploy"

## Passo 4: Configurar Secrets (Variáveis de Ambiente)

Depois que a app fizer deploy:

1. Na sua app, clique em "Settings" (engrenagem no canto superior direito)
2. Clique em "Secrets"
3. Adicione:

```toml
NOME_FUNCIONARIO = "Francisco Osvaldo Lima Holanda"
ID_FUNCIONARIO = "2445201"
TELEFONE = "85988449973"
```

4. Salve

## Resultado Final

Sua app estará em: `https://seu-usuario-automacao-forms.streamlit.app`

E pode ser acessada do celular, PC, qualquer lugar! ✅

## Troubleshooting

Se a app demorar para carregar:
- Streamlit Cloud instala dependências na primeira execução
- Pode levar 1-2 minutos
- Próximas execuções são mais rápidas

Se houver erro com Playwright:
- Streamlit Cloud instalará automaticamente os binários
- Sem necessidade de configuração extra
