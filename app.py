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

# ==================== SEUS DADOS E CONFIGURAÇÕES (RESTAURADOS) ====================
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

# ==================== LÓGICA DE NEGÓCIO ORIGINAL ====================

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
        encontrou_preferido = False
        for bairro_pref_norm, bairro_pref_original in bairros_pref_normalizados.items():
            if bairro_pref_norm in rota_norm:
                rotas_preferidas.append((BAIRROS_PREFERIDOS.index(bairro_pref_original), rota))
                encontrou_preferido = True
                break
        if not encontrou_preferido:
            rotas_restantes.append(rota)
            
    rotas_preferidas.sort(key=lambda x: x[0])
    return [r for _, r in rotas_preferidas] + rotas_restantes

# ==================== ENGINE DE AUTOMAÇÃO ====================

@st.cache_resource
def setup_playwright():
    """Instala os binários necessários no Streamlit Cloud."""
    subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)

def executar_envio(url, rota, placeholder):
    setup_playwright()
    with sync_playwright() as p:
        # Args robustos para evitar o TargetClosedError em containers
        browser = p.chromium.launch(
            headless=True, 
            args=[
                "--no-sandbox", 
                "--disable-dev-shm-usage", 
                "--disable-gpu",
                "--disable-setuid-sandbox"
            ]
        )
        page = browser.new_page()
        
        try:
            placeholder.write(f"🔄 Enviar: **{rota}**")
            page.goto(url, wait_until="networkidle", timeout=60000)
            
            # P1: Identificação
            inputs = page.locator("input[type='text'], input[type='number'], input[type='tel']")
            inputs.nth(0).fill(NOME)
            inputs.nth(1).fill(ID_FUNC)
            page.get_by_role("button", name=re.compile(r"Avançar|Próxima|Next", re.IGNORECASE)).click()
            
            # P2: Seleção Rota
            page.wait_for_selector("[role='listbox']", timeout=15000)
            page.locator("[role='listbox']").click()
            page.get_by_role("option", name=rota, exact=True).click()
            page.get_by_role("button", name=re.compile(r"Avançar|Próxima|Next", re.IGNORECASE)).click()
            
            # P3: Telefone
            page.wait_for_selector("input[type='text'], input[type='tel']", timeout=10000)
            page.locator("input[type='text'], input[type='tel']").first.fill(TELEFONE)
            page.get_by_role("button", name=re.compile(r"Enviar|Submit", re.IGNORECASE)).click()
            
            # Confirmação
            page.wait_for_selector("text=registrada", timeout=10000)
            return True
        except Exception as e:
            st.error(f"Falha na rota {rota}: {e}")
            return False
        finally:
            browser.close()

# ==================== INTERFACE ====================

st.title("🚀 SPX Automator")

if not all([NOME, ID_FUNC, TELEFONE]):
    st.error("Configure NOME_FUNCIONARIO, ID_FUNCIONARIO e TELEFONE nos Secrets.")
    st.stop()

url_forms = st.text_input("URL do Formulário:")

if "fila_rotas" not in st.session_state:
    st.session_state.fila_rotas = []

col1, col2 = st.columns(2)

if col1.button("🔍 1. Mapear Rotas"):
    if not url_forms:
        st.warning("Insira a URL.")
    else:
        setup_playwright()
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
            page = browser.new_page()
            try:
                page.goto(url_forms)
                inputs = page.locator("input[type='text'], input[type='number']")
                inputs.nth(0).fill(NOME)
                inputs.nth(1).fill(ID_FUNC)
                page.get_by_role("button", name=re.compile(r"Avançar|Próxima", re.IGNORECASE)).click()
                
                page.wait_for_selector("[role='listbox']")
                page.locator("[role='listbox']").click()
                opcoes = page.locator("[role='option']").all_inner_texts()
                
                bairros_limpos = [remover_acentos(b) for b in MEUS_BAIRROS]
                encontradas = [opt for opt in opcoes if any(bl in remover_acentos(opt) for bl in bairros_limpos) and remover_acentos(opt) != "escolher"]
                
                st.session_state.fila_rotas = ordenar_rotas_por_preferencia(encontradas)
            except Exception as e:
                st.error(f"Erro no mapeamento: {e}")
            finally:
                browser.close()

if st.session_state.fila_rotas:
    st.write("### 📋 Fila de Envio:")
    st.info(", ".join(st.session_state.fila_rotas))
    
    if col2.button("▶️ 2. Iniciar Envios", type="primary"):
        progresso = st.progress(0)
        status_msg = st.empty()
        sucessos = 0
        total = len(st.session_state.fila_rotas)
        
        for idx, rota in enumerate(st.session_state.fila_rotas, 1):
            if executar_envio(url_forms, rota, status_msg):
                sucessos += 1
            progresso.progress(idx / total)
            time.sleep(1)
            
        st.success(f"Concluído: {sucessos}/{total} enviadas.")