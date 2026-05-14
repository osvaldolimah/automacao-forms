import streamlit as st
import os
import time
import unicodedata
import re
import subprocess
import sys
from typing import List
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

# --- CONFIGURAÇÃO E DADOS (RESTAURADOS) ---
load_dotenv()

NOME = st.secrets.get("NOME_FUNCIONARIO", os.getenv("NOME_FUNCIONARIO", ""))
ID_FUNC = st.secrets.get("ID_FUNCIONARIO", os.getenv("ID_FUNCIONARIO", ""))
TELEFONE = st.secrets.get("TELEFONE", os.getenv("TELEFONE", ""))

MEUS_BAIRROS = [
    "Cambeba", "Guararapes", "Benfica", "Itaperi", "Rodolfo Teófilo", "Cajazeiras",
    "Aerolândia", "Alto da Balança", "Boa Vista", "Luciano Cavalcante",
    "Dias Macedo", "Damas", "Montese", "Jardim América", "Parreão",
    "Fátima", "Serrinha", "Itaperi", "Cidade dos Funcionários",
    "Parque Iracema", "Parque Manibura", "Parquelandia", "Amadeu Furtado",
    "Rodolfo Teofilo", "São Gerardo", "Bom Futuro", "Vila União"
]

BAIRROS_PREFERIDOS = [
    "Parque Iracema", "Cajazeiras", "Cambeba", "Damas", "Itaperi",
    "Guararapes", "Luciano Cavalcante"
]

# --- LÓGICA DE NEGÓCIO ---

def remover_acentos(texto: str) -> str:
    if not texto: return ""
    nfkd = unicodedata.normalize('NFKD', texto)
    return "".join([c for c in nfkd if not unicodedata.combining(c)]).lower().strip()

def ordenar_rotas_por_preferencia(rotas: List[str]) -> List[str]:
    rotas_preferidas = []
    rotas_restantes = []
    bairros_pref_normalizados = {remover_acentos(b): b for b in BAIRROS_PREFERIDOS}
    
    for rota in rotas:
        rota_norm = remover_acentos(rota)
        match = next((orig for norm, orig in bairros_pref_normalizados.items() if norm in rota_norm), None)
        if match:
            rotas_preferidas.append((BAIRROS_PREFERIDOS.index(match), rota))
        else:
            rotas_restantes.append(rota)
            
    rotas_preferidas.sort(key=lambda x: x[0])
    return [r for _, r in rotas_preferidas] + rotas_restantes

@st.cache_resource
def setup_browser():
    subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)

# --- ENGINE DE AUTOMAÇÃO ---

def executar_envio(url, rota, status_placeholder):
    setup_browser()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
        context = browser.new_context()
        page = context.new_page()
        
        try:
            status_placeholder.write(f"🔄 Processando: **{rota}**")
            page.goto(url, wait_until="networkidle")
            
            # P1: Identificação
            inputs = page.locator("input[type='text'], input[type='number'], input[type='tel']")
            inputs.nth(0).fill(NOME)
            inputs.nth(1).fill(ID_FUNC)
            page.get_by_role("button", name=re.compile(r"Avançar|Próxima|Next", re.IGNORECASE)).click()
            
            # P2: Seleção de Rota
            page.wait_for_selector("[role='listbox']", timeout=10000)
            page.locator("[role='listbox']").click()
            page.get_by_role("option", name=rota, exact=True).click()
            page.get_by_role("button", name=re.compile(r"Avançar|Próxima|Next", re.IGNORECASE)).click()
            
            # P3: Telefone
            page.wait_for_selector("input[type='text'], input[type='tel']", timeout=5000)
            page.locator("input[type='text'], input[type='tel']").first.fill(TELEFONE)
            page.get_by_role("button", name=re.compile(r"Enviar|Submit", re.IGNORECASE)).click()
            
            # Sucesso
            page.wait_for_selector("text=registrada", timeout=10000)
            return True
        except Exception as e:
            st.error(f"Erro em {rota}: {str(e)}")
            return False
        finally:
            browser.close()

# --- INTERFACE STREAMLIT ---

st.title("🚀 Automação SPX Express")

if not all([NOME, ID_FUNC, TELEFONE]):
    st.error("Configure os Secrets (NOME_FUNCIONARIO, ID_FUNCIONARIO, TELEFONE)")
    st.stop()

url_input = st.text_input("URL do Forms:")

if "lista_final" not in st.session_state:
    st.session_state.lista_final = []

if st.button("🔍 Mapear e Ordenar Rotas"):
    setup_browser()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = browser.new_page()
        page.goto(url_input)
        
        # Preenche P1 para chegar nas rotas
        inputs = page.locator("input[type='text'], input[type='number']")
        inputs.nth(0).fill(NOME)
        inputs.nth(1).fill(ID_FUNC)
        page.get_by_role("button", name=re.compile(r"Avançar|Próxima", re.IGNORECASE)).click()
        
        # Mapeia opções
        page.wait_for_selector("[role='listbox']")
        page.locator("[role='listbox']").click()
        opcoes = page.locator("[role='option']").all_inner_texts()
        
        bairros_limpos = [remover_acentos(b) for b in MEUS_BAIRROS]
        encontradas = [opt for opt in opcoes if any(bl in remover_acentos(opt) for bl in bairros_limpos) and remover_acentos(opt) != "escolher"]
        
        st.session_state.lista_final = ordenar_rotas_por_preferencia(encontradas)
        browser.close()

if st.session_state.lista_final:
    st.write(f"### 📋 {len(st.session_state.lista_final)} Rotas na Fila:")
    st.info(", ".join(st.session_state.lista_final))
    
    if st.button("▶️ Iniciar Envio em Massa"):
        progresso = st.progress(0)
        status_txt = st.empty()
        sucessos = 0
        
        for i, rota in enumerate(st.session_state.lista_final, 1):
            if executar_envio(url_input, rota, status_txt):
                sucessos += 1
            progresso.progress(i / len(st.session_state.lista_final))
            time.sleep(1)
            
        st.success(f"🏁 Finalizado! {sucessos}/{len(st.session_state.lista_final)} enviadas.")