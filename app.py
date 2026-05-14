import streamlit as st
import os
import subprocess
import sys
import re
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

# Carregar variáveis de ambiente (Secrets no Streamlit Cloud)
load_dotenv()
NOME = st.secrets.get("NOME_FUNCIONARIO", os.getenv("NOME_FUNCIONARIO", ""))
ID_FUNC = st.secrets.get("ID_FUNCIONARIO", os.getenv("ID_FUNCIONARIO", ""))
TELEFONE = st.secrets.get("TELEFONE", os.getenv("TELEFONE", ""))

@st.cache_resource
def instalar_browser():
    """Instala o binário do Chromium sem depender do apt-get do sistema."""
    subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)

def executar_automacao(url, rota):
    instalar_browser()
    with sync_playwright() as p:
        # Lançamento do browser com argumentos para ambiente Cloud
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-gpu"])
        page = browser.new_page()
        
        try:
            page.goto(url, wait_until="networkidle")
            
            # Passo 1: Identificação (usando seletores genéricos robustos)
            inputs = page.locator("input[type='text'], input[type='number'], input[type='tel']")
            inputs.nth(0).fill(NOME)
            inputs.nth(1).fill(ID_FUNC)
            
            # Clique no botão (Regex resolve o erro da lista que deu no log)
            page.get_by_role("button", name=re.compile(r"Avançar|Próxima|Next", re.IGNORECASE)).click()
            
            # Passo 2: Seleção da Rota
            page.wait_for_selector("[role='listbox']", timeout=10000)
            page.locator("[role='listbox']").click()
            
            # Seleciona a rota exata
            page.get_by_role("option", name=rota, exact=True).click()
            
            # Avança novamente
            page.get_by_role("button", name=re.compile(r"Avançar|Próxima|Next", re.IGNORECASE)).click()
            
            # Passo 3: Telefone e Envio
            page.wait_for_selector("input[type='text'], input[type='tel']", timeout=5000)
            page.locator("input[type='text'], input[type='tel']").first.fill(TELEFONE)
            
            page.get_by_role("button", name=re.compile(r"Enviar|Submit", re.IGNORECASE)).click()
            
            # Validação de sucesso
            page.wait_for_selector("text=registrada", timeout=10000)
            return True
        except Exception as e:
            st.error(f"Erro na rota {rota}: {str(e)}")
            return False
        finally:
            browser.close()

# --- Interface ---
st.title("🚀 Automação SPX")

url = st.text_input("URL do Forms:")
rota_teste = "Cambeba" # Exemplo, você pode carregar sua lista aqui

if st.button("Executar"):
    if not url:
        st.error("Insira a URL")
    else:
        with st.spinner(f"Enviando para {rota_teste}..."):
            sucesso = executar_automacao(url, rota_teste)
            if sucesso:
                st.success("Enviado com sucesso!")