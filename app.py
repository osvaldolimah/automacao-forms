import streamlit as st
import unicodedata
import os
import subprocess
import sys
from pathlib import Path
from typing import List
from urllib.parse import urlparse
from dotenv import load_dotenv

# MUDANÇA: Usando a API Síncrona para estabilidade no Streamlit
from playwright.sync_api import sync_playwright

# Configuração de Ambiente
load_dotenv()
NOME = os.getenv("NOME_FUNCIONARIO", "").strip()
ID_FUNC = os.getenv("ID_FUNCIONARIO", "").strip()
TELEFONE = os.getenv("TELEFONE", "").strip()

# Listas de Bairros (Mantidas do seu original)
MEUS_BAIRROS = ["Cambeba", "Guararapes", "Benfica", "Itaperi", "Rodolfo Teófilo", "Cajazeiras", "Aerolândia", "Alto da Balança", "Boa Vista", "Luciano Cavalcante", "Dias Macedo", "Damas", "Montese", "Jardim América", "Parreão", "Fátima", "Serrinha", "Cidade dos Funcionários", "Parque Iracema", "Parque Manibura", "Parquelandia", "Amadeu Furtado", "São Gerardo", "Bom Futuro", "Vila União"]
BAIRROS_PREFERIDOS = ["Parque Iracema", "Cajazeiras", "Cambeba", "Damas", "Itaperi", "Guararapes", "Luciano Cavalcante"]

@st.cache_resource(show_spinner=False)
def garantir_chromium_playwright():
    """Garante os binários do browser sem travar o app."""
    try:
        # Tenta rodar o install. Se já existir, ele é rápido.
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
    except Exception as e:
        st.error(f"Erro ao instalar Chromium: {e}")

def remover_acentos(texto: str) -> str:
    return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn').lower()

def _playwright_launch_args():
    return {
        "headless": True,
        "args": ["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"]
    }

def obter_rotas_disponiveis(url, progress_placeholder):
    garantir_chromium_playwright()
    
    with sync_playwright() as p:
        browser = p.chromium.launch(**_playwright_launch_args())
        page = browser.new_page()
        
        try:
            progress_placeholder.info("📄 Abrindo formulário...")
            page.goto(url, wait_until="networkidle")
            
            # Preenchimento Inicial
            inputs = page.locator("input[type='text'], input[type='tel'], input[type='number']")
            if inputs.count() < 2: return []
            
            inputs.nth(0).fill(NOME)
            inputs.nth(1).fill(ID_FUNC)
            
            # Avançar
            page.get_by_role("button", name=["Avançar", "Próxima", "Next"]).click()
            page.wait_for_selector("[role='listbox']", timeout=15000)
            
            # Extrair Rotas
            page.locator("[role='listbox']").click()
            page.wait_for_selector("[role='option']", timeout=5000)
            
            opcoes = page.locator("[role='option']").all_inner_texts()
            meus_bairros_limpos = [remover_acentos(b) for b in MEUS_BAIRROS]
            
            rotas_encontradas = []
            for texto in opcoes:
                texto_limpo = remover_acentos(texto)
                if any(b in texto_limpo for b in meus_bairros_limpos) and texto_limpo != "escolher":
                    rotas_encontradas.append(texto.strip())
            
            return list(dict.fromkeys(rotas_encontradas)) # Remove duplicatas
        finally:
            browser.close()

# UI do Streamlit simplificada para o teste
st.title("🚀 Automação de Rotas")

url = st.text_input("URL do Forms:")
if st.button("Buscar Rotas"):
    if url:
        placeholder = st.empty()
        rotas = obter_rotas_disponiveis(url, placeholder)
        if rotas:
            st.write(f"Encontradas {len(rotas)} rotas:")
            st.success(", ".join(rotas))
        else:
            st.warning("Nenhuma rota encontrada.")