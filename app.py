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

# ==================== SEUS DADOS ORIGINAIS (RESTAURADOS) ====================
load_dotenv()

# Prioriza st.secrets (para o Cloud) mas aceita .env (local)
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

# ==================== LÓGICA DE NEGÓCIO (RESTAURADA) ====================

def remover_acentos(texto: str) -> str:
    if not texto: return ""
    nfkd_form = unicodedata.normalize('NFKD', texto)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)]).lower().strip()

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
    return [rota for _, rota in rotas_preferidas] + rotas_restantes

# ==================== ENGINE DE AUTOMAÇÃO (CORRIGIDA) ====================

@st.cache_resource
def instalar_playwright():
    """Garante que os binários do browser existam no servidor."""
    subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)

def executar_fluxo_formulario(url, rota_alvo, status_placeholder):
    instalar_playwright()
    with sync_playwright() as p:
        # A flag --disable-dev-shm-usage resolve o TargetClosedError no Cloud
        browser = p.chromium.launch(
            headless=True, 
            args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu", "--disable-setuid-sandbox"]
        )
        context = browser.new_context()
        page = context.new_page()
        
        try:
            status_placeholder.info(f"🚚 Processando rota: {rota_alvo}")
            page.goto(url, wait_until="networkidle", timeout=60000)
            
            # PÁGINA 1: Identificação
            inputs = page.locator("input[type='text'], input[type='number'], input[type='tel']")
            inputs.nth(0).fill(NOME)
            inputs.nth(1).fill(ID_FUNC)
            
            # Regex evita o erro de 'list has no replace'
            btn_avancar = page.get_by_role("button", name=re.compile(r"Avançar|Próxima|Next", re.IGNORECASE))
            btn_avancar.click()
            
            # PÁGINA 2: Seleção de Rota
            page.wait_for_selector("[role='listbox']", timeout=15000)
            page.locator("[role='listbox']").click()
            
            # Clica na opção que contém o nome da rota
            page.get_by_role("option", name=rota_alvo, exact=True).click()
            
            # Avançar para página de telefone
            btn_avancar.click()
            
            # PÁGINA 3: Telefone e Enviar
            page.wait_for_selector("input[type='text'], input[type='tel']", timeout=10000)
            page.locator("input[type='text'], input[type='tel']").first.fill(TELEFONE)
            
            btn_enviar = page.get_by_role("button", name=re.compile(r"Enviar|Submit", re.IGNORECASE))
            btn_enviar.click()
            
            # Confirmação de Sucesso
            page.wait_for_selector("text=registrada", timeout=10000)
            return True
        except Exception as e:
            st.error(f"Erro ao enviar {rota_alvo}: {str(e)}")
            return False
        finally:
            browser.close()

# ==================== INTERFACE STREAMLIT ====================

st.title("🚀 Automação Forms")

if not all([NOME, ID_FUNC, TELEFONE]):
    st.error("Credenciais não encontradas nos Secrets ou no .env")
    st.stop()

url_forms = st.text_input("Cole a URL do Forms:")

if "rotas_preparadas" not in st.session_state:
    st.session_state.rotas_preparadas = []

col1, col2 = st.columns(2)

if col1.button("🔍 Mapear Rotas"):
    if not url_forms:
        st.warning("Insira a URL primeiro.")
    else:
        instalar_playwright()
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
            page = browser.new_page()
            page.goto(url_forms)
            
            # Passo 1 rápido para ler o dropdown
            inputs = page.locator("input[type='text'], input[type='number']")
            inputs.nth(0).fill(NOME)
            inputs.nth(1).fill(ID_FUNC)
            page.get_by_role("button", name=re.compile(r"Avançar|Próxima", re.IGNORECASE)).click()
            
            page.wait_for_selector("[role='listbox']")
            page.locator("[role='listbox']").click()
            time.sleep(1)
            
            opcoes = page.locator("[role='option']").all_inner_texts()
            meus_bairros_limpos = [remover_acentos(b) for b in MEUS_BAIRROS]
            
            encontradas = [
                opt for opt in opcoes 
                if any(bl in remover_acentos(opt) for bl in meus_bairros_limpos) 
                and remover_acentos(opt) != "escolher"
            ]
            
            st.session_state.rotas_preparadas = ordenar_rotas_por_preferencia(encontradas)
            browser.close()

if st.session_state.rotas_preparadas:
    st.write(f"### 📋 {len(st.session_state.rotas_preparadas)} Rotas prontas para envio:")
    st.info(", ".join(st.session_state.rotas_preparadas))
    
    if col2.button("▶️ Iniciar Envio Total", type="primary"):
        progresso = st.progress(0)
        status_msg = st.empty()
        sucessos = 0
        total = len(st.session_state.rotas_preparadas)
        
        for idx, rota in enumerate(st.session_state.rotas_preparadas, 1):
            if executar_fluxo_formulario(url_forms, rota, status_msg):
                sucessos += 1
            progresso.progress(idx / total)
            time.sleep(2)
            
        st.success(f"🏁 Concluído: {sucessos}/{total} enviadas com sucesso.")