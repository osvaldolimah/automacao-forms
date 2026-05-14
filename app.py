import streamlit as st
import os
import time
import unicodedata
from typing import List
from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

# ==================== CONFIGS E ESTADO ====================
st.set_page_config(page_title="SPX Route Automator", page_icon="🚚")

load_dotenv()
NOME = os.getenv("NOME_FUNCIONARIO", "").strip()
ID_FUNC = os.getenv("ID_FUNCIONARIO", "").strip()
TELEFONE = os.getenv("TELEFONE", "").strip()

# Inicialização do Session State
if "rotas_disponiveis" not in st.session_state:
    st.session_state.rotas_disponiveis = []
if "log_execucao" not in st.session_state:
    st.session_state.log_execucao = []

# Bairros (Mantidos do seu core original)
MEUS_BAIRROS = ["Cambeba", "Guararapes", "Benfica", "Itaperi", "Rodolfo Teófilo", "Cajazeiras", "Aerolândia", "Alto da Balança", "Boa Vista", "Luciano Cavalcante", "Dias Macedo", "Damas", "Montese", "Jardim América", "Parreão", "Fátima", "Serrinha", "Cidade dos Funcionários", "Parque Iracema", "Parque Manibura", "Parquelandia", "Amadeu Furtado", "São Gerardo", "Bom Futuro", "Vila União"]
BAIRROS_PREFERIDOS = ["Parque Iracema", "Cajazeiras", "Cambeba", "Damas", "Itaperi", "Guararapes", "Luciano Cavalcante"]

# ==================== UTILITÁRIOS ====================

def remover_acentos(texto: str) -> str:
    if not texto: return ""
    return "".join([c for c in unicodedata.normalize('NFKD', texto) if not unicodedata.combining(c)]).lower().strip()

def ordenar_preferencia(rotas: List[str]) -> List[str]:
    pref_norm = {remover_acentos(b): b for b in BAIRROS_PREFERIDOS}
    rotas_pref = []
    rotas_rest = []
    
    for r in rotas:
        r_norm = remover_acentos(r)
        match = next((b for b_norm, b in pref_norm.items() if b_norm in r_norm), None)
        if match:
            rotas_pref.append((BAIRROS_PREFERIDOS.index(match), r))
        else:
            rotas_rest.append(r)
    
    rotas_pref.sort(key=lambda x: x[0])
    return [r for _, r in rotas_pref] + rotas_rest

@st.cache_resource
def get_driver_path():
    """Instala o driver uma única vez e cacheia o caminho."""
    return ChromeDriverManager().install()

def criar_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    # Evita detecção básica de bot
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    return webdriver.Chrome(service=Service(get_driver_path()), options=options)

def preencher_e_avancar(driver, wait, inputs_data: list, is_final=False):
    """Lógica genérica para preencher inputs por índice e clicar no botão de ação."""
    inputs = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//input[@type='text' or @type='number' or @type='tel']")))
    for idx, texto in inputs_data:
        campo = inputs[idx]
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", campo)
        campo.clear()
        campo.send_keys(texto)
    
    btn_text = "Enviar" if is_final else "Avançar"
    btn_xpath = f"//span[normalize-space(text())='{btn_text}' or normalize-space(text())='Próxima']"
    btn = wait.until(EC.element_to_be_clickable((By.XPATH, btn_xpath)))
    driver.execute_script("arguments[0].click();", btn)

# ==================== UI ====================

st.title("🚚 Automação SPX Express")
st.caption("Mapeamento e envio em massa para formulários Google")

url_forms = st.text_input("URL do Formulário:", placeholder="https://docs.google.com/forms/...")

col1, col2 = st.columns(2)

# --- AÇÃO 1: MAPEAMENTO ---
if col1.button("🔍 1. Mapear Rotas", use_container_width=True):
    if not url_forms:
        st.error("Insira a URL.")
    else:
        with st.status("Vasculhando rotas...", expanded=True) as status:
            driver = criar_driver()
            try:
                wait = WebDriverWait(driver, 15)
                driver.get(url_forms)
                
                # Pag 1: Identificação
                preencher_e_avancar(driver, wait, [(0, NOME), (1, ID_FUNC)])
                
                # Pag 2: Dropdown
                time.sleep(1.5)
                dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@role='listbox']")))
                driver.execute_script("arguments[0].click();", dropdown)
                
                time.sleep(1)
                opcoes = driver.find_elements(By.XPATH, "//div[@role='option']")
                bairros_limpos = [remover_acentos(b) for b in MEUS_BAIRROS]
                
                encontradas = []
                for opt in opcoes:
                    val = opt.get_attribute("data-value") or opt.text
                    if val and val != "Escolher":
                        if any(bl in remover_acentos(val) for bl in bairros_limpos):
                            encontradas.append(val)
                
                st.session_state.rotas_disponiveis = ordenar_preferencia(encontradas)
                status.update(label=f"Mapeamento concluído: {len(encontradas)} rotas.", state="complete")
            except Exception as e:
                st.error(f"Erro no mapeamento: {e}")
            finally:
                driver.quit()

# --- AÇÃO 2: EXECUÇÃO ---
if st.session_state.rotas_disponiveis:
    st.write("### 📍 Rotas Detectadas")
    st.info(", ".join(st.session_state.rotas_disponiveis))
    
    if col2.button("🚀 2. Iniciar Envios", type="primary", use_container_width=True):
        progress = st.progress(0)
        total = len(st.session_state.rotas_disponiveis)
        
        for i, rota in enumerate(st.session_state.rotas_disponiveis, 1):
            with st.spinner(f"Processando {rota}..."):
                driver = criar_driver()
                try:
                    wait = WebDriverWait(driver, 20)
                    driver.get(url_forms)
                    
                    # P1
                    preencher_e_avancar(driver, wait, [(0, NOME), (1, ID_FUNC)])
                    
                    # P2: Seleção Rota
                    time.sleep(1.2)
                    dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@role='listbox']")))
                    driver.execute_script("arguments[0].click();", dropdown)
                    time.sleep(0.8)
                    
                    opt_xpath = f"//div[@role='option']//span[text()='{rota}']"
                    option_el = wait.until(EC.element_to_be_clickable((By.XPATH, opt_xpath)))
                    driver.execute_script("arguments[0].click();", option_el)
                    
                    time.sleep(0.5)
                    btn_next = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[normalize-space(text())='Avançar' or normalize-space(text())='Próxima']")))
                    driver.execute_script("arguments[0].click();", btn_next)
                    
                    # P3: Telefone e Envio
                    time.sleep(1.2)
                    preencher_e_avancar(driver, wait, [(0, TELEFONE)], is_final=True)
                    
                    # Confirmação
                    wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'registrada') or contains(text(), 'agradecemos')]")))
                    st.toast(f"Sucesso: {rota}")
                except Exception as e:
                    st.error(f"Falha na rota {rota}: {e}")
                finally:
                    driver.quit()
            
            progress.progress(i / total)
            time.sleep(1) # Delay humano entre sessões

        st.success("✅ Processo finalizado!")