import logging
import os
import time
import unicodedata
from typing import List
from urllib.parse import urlparse

import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="Automação Google Forms",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==================== CSS CUSTOMIZADO ====================
st.markdown("""
<style>
    .stTextArea textarea { font-family: monospace; font-size: 0.82rem; }
    .log-box { background: #0e1117; color: #00ff88; font-family: monospace;
               font-size: 0.80rem; padding: 12px; border-radius: 8px;
               max-height: 350px; overflow-y: auto; white-space: pre-wrap; }
    .metric-success { color: #00c853; font-weight: bold; }
    .metric-error   { color: #ff5252; font-weight: bold; }
    .rota-tag { display: inline-block; background: #1e3a5f; color: #90caf9;
                border-radius: 4px; padding: 2px 8px; margin: 2px;
                font-size: 0.82rem; }
</style>
""", unsafe_allow_html=True)

# ==================== CONSTANTES ====================
TIMEOUT_PADRAO = 15
TIMEOUT_ENVIO = 20
INTERVALO_ENTRE_ENVIOS = 3
MAX_TENTATIVAS = 2
INTERVALO_RETRY = 2

BAIRROS_DEFAULT = [
    "Cambeba", "Guararapes", "Benfica", "Itaperi", "Rodolfo Teófilo", "Cajazeiras",
    "Aerolândia", "Alto da Balança", "Boa Vista", "Luciano Cavalcante",
    "Dias Macedo", "Damas", "Montese", "Jardim América", "Parreão",
    "Fátima", "Serrinha", "Cidade dos Funcionários", "Parque Iracema",
    "Parque Manibura", "Parquelandia", "Amadeu Furtado", "Rodolfo Teofilo",
    "São Gerardo", "Bom Futuro", "Vila União"
]

BAIRROS_PREFERIDOS_DEFAULT = [
    "Parque Iracema", "Cajazeiras", "Cambeba", "Damas",
    "Itaperi", "Guararapes", "Luciano Cavalcante"
]

# ==================== SESSION STATE ====================
def init_state():
    defaults = {
        "rotas_disponiveis": [],
        "rotas_selecionadas": [],
        "resultado": {},
        "logs": [],
        "fase": "idle",  # idle | mapeado | enviando | concluido
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ==================== LOGGING PARA STREAMLIT ====================
def make_log_fn(placeholder):
    """Retorna uma função de log que atualiza o placeholder em tempo real."""
    def log(msg: str, nivel: str = "INFO"):
        icons = {"INFO": "ℹ️", "OK": "✅", "ERRO": "❌", "WARN": "⚠️",
                 "PROC": "⚙️", "RETRY": "🔁", "WAIT": "⏳", "MAP": "🗺️"}
        icon = icons.get(nivel, "•")
        entry = f"{icon} {msg}"
        st.session_state.logs.append(entry)
        content = "\n".join(st.session_state.logs[-100:])  # Últimas 100 linhas
        placeholder.markdown(f'<div class="log-box">{content}</div>', unsafe_allow_html=True)
    return log

# ==================== FUNÇÕES AUXILIARES ====================
def remover_acentos(texto: str) -> str:
    if not texto:
        return ""
    nfkd = unicodedata.normalize('NFKD', texto)
    return "".join([c for c in nfkd if not unicodedata.combining(c)]).lower().strip()


def validar_url(url: str) -> bool:
    try:
        result = urlparse(url)
        if not result.scheme or not result.netloc:
            return False
        if "docs.google.com/forms" not in url and "forms.gle" not in url:
            return False
        return True
    except Exception:
        return False


def safe_click(driver: webdriver.Chrome, element) -> None:
    try:
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(0.3)
        element.click()
    except Exception:
        driver.execute_script("arguments[0].click();", element)


def preencher_input(driver, wait, index: int, texto: str) -> None:
    inputs = wait.until(EC.presence_of_all_elements_located(
        (By.XPATH, "//input[@type='text' or @type='number']")
    ))
    campo = inputs[index]
    safe_click(driver, campo)
    campo.clear()
    campo.send_keys(texto)


def ordenar_rotas_por_preferencia(rotas: List[str], bairros_preferidos: List[str]) -> List[str]:
    bairros_pref_norm = {remover_acentos(b): b for b in bairros_preferidos}
    rotas_preferidas, rotas_restantes = [], []
    for rota in rotas:
        rota_norm = remover_acentos(rota)
        encontrou = False
        for bp_norm, bp_orig in bairros_pref_norm.items():
            if bp_norm in rota_norm:
                rotas_preferidas.append((bairros_preferidos.index(bp_orig), rota))
                encontrou = True
                break
        if not encontrou:
            rotas_restantes.append(rota)
    rotas_preferidas.sort(key=lambda x: x[0])
    return [r for _, r in rotas_preferidas] + rotas_restantes

# ==================== SELENIUM ====================
def criar_driver() -> webdriver.Chrome:
    """
    Cria o ChromeDriver com suporte a ambiente local e Streamlit Cloud.
    Headless é sempre ativado (obrigatório em ambiente cloud/server).
    """
    options = webdriver.ChromeOptions()

    # ── Modo headless ─────────────────────────────────────────────────────────
    options.add_argument("--headless=new")

    # ── Flags essenciais para ambientes container / cloud ─────────────────────
    options.add_argument("--no-sandbox")               # Sem sandbox do kernel
    options.add_argument("--disable-setuid-sandbox")   # Sandbox extra desativada
    options.add_argument("--no-zygote")                # Sem processo zygote (crítico em Docker)
    options.add_argument("--disable-dev-shm-usage")    # Usa /tmp em vez de /dev/shm (limitado no cloud)

    # ── GPU / renderização ────────────────────────────────────────────────────
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--disable-accelerated-2d-canvas")
    options.add_argument("--disable-gl-drawing-for-tests")

    # ── Estabilidade geral ────────────────────────────────────────────────────
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-plugins")
    options.add_argument("--disable-sync")
    options.add_argument("--disable-background-networking")
    options.add_argument("--disable-default-apps")
    options.add_argument("--disable-hang-monitor")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-translate")
    options.add_argument("--metrics-recording-only")
    options.add_argument("--safebrowsing-disable-auto-update")
    options.add_argument("--log-level=3")
    options.add_argument("--disable-logging")
    options.add_argument("--remote-debugging-port=0")
    options.add_argument("--single-process")           # Um único processo (mais estável em cloud)

    # Caminhos conhecidos de binário do Chromium por distro
    CHROME_BINARIES = [
        "/usr/bin/chromium",           # Debian Trixie (Streamlit Cloud)
        "/usr/bin/chromium-browser",   # Ubuntu / Debian Bullseye
        "/usr/bin/google-chrome",      # Google Chrome
        "/usr/bin/google-chrome-stable",
    ]
    # Caminhos conhecidos do ChromeDriver
    CHROMEDRIVER_PATHS = [
        "/usr/bin/chromedriver",                      # Debian Trixie
        "/usr/lib/chromium/chromedriver",             # Algumas distros
        "/usr/lib/chromium-browser/chromedriver",     # Ubuntu older
    ]

    # Detecta se está em ambiente cloud (sem webdriver-manager disponível ou sem rede)
    chrome_bin  = next((p for p in CHROME_BINARIES    if os.path.exists(p)), None)
    driver_bin  = next((p for p in CHROMEDRIVER_PATHS if os.path.exists(p)), None)

    if chrome_bin and driver_bin:
        # Ambiente cloud/server: usa binários do sistema
        options.binary_location = chrome_bin
        return webdriver.Chrome(service=Service(driver_bin), options=options)

    # Fallback local: webdriver-manager (faz download automático)
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        logging.getLogger('webdriver_manager').setLevel(logging.WARNING)
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)
    except Exception as e:
        raise RuntimeError(
            f"Chrome/Chromium não encontrado ({e}). "
            "Cloud: certifique-se que packages.txt contém 'chromium' e 'chromium-driver'. "
            "Local: instale o Chrome ou adicione webdriver-manager ao requirements.txt."
        )


def obter_rotas_disponiveis(
    url: str, nome: str, id_func: str,
    meus_bairros: List[str], log
) -> List[str]:
    driver = None
    try:
        log("Iniciando ChromeDriver para mapeamento...", "MAP")
        driver = criar_driver()
        wait = WebDriverWait(driver, TIMEOUT_PADRAO)
        rotas_encontradas = []
        bairros_limpos = [remover_acentos(b) for b in meus_bairros]

        driver.get(url)
        log("Página carregada. Preenchendo identificação...", "MAP")

        preencher_input(driver, wait, 0, nome)
        preencher_input(driver, wait, 1, id_func)

        btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//span[normalize-space(text())='Avançar' or normalize-space(text())='Próxima']")
        ))
        safe_click(driver, btn)
        log("Avançou para página 2 (seleção de rota).", "MAP")

        time.sleep(2)
        dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@role='listbox']")))
        safe_click(driver, dropdown)
        time.sleep(2)

        opcoes = driver.find_elements(By.XPATH, "//div[@role='option']")
        log(f"Total de opções no dropdown: {len(opcoes)}", "MAP")

        for opt in opcoes:
            texto_original = opt.get_attribute("data-value") or opt.text
            if texto_original and texto_original != "Escolher":
                texto_limpo = remover_acentos(texto_original)
                if any(b in texto_limpo for b in bairros_limpos):
                    rotas_encontradas.append(texto_original)
                    log(f"Rota encontrada: {texto_original}", "OK")

        log(f"Mapeamento concluído — {len(rotas_encontradas)} rota(s) compatível(is).", "INFO")
        return rotas_encontradas

    except Exception as e:
        log(f"Erro no mapeamento: {e}", "ERRO")
        return []
    finally:
        if driver:
            driver.quit()


def enviar_formulario(
    url: str, rota: str, nome: str, id_func: str, telefone: str,
    log, tentativa: int = 1
) -> bool:
    driver = None
    try:
        log(f"[Tentativa {tentativa}/{MAX_TENTATIVAS}] Iniciando envio: {rota}", "PROC")
        driver = criar_driver()
        wait = WebDriverWait(driver, TIMEOUT_ENVIO)

        driver.get(url)

        # Página 1: Identificação
        preencher_input(driver, wait, 0, nome)
        preencher_input(driver, wait, 1, id_func)
        btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//span[normalize-space(text())='Avançar' or normalize-space(text())='Próxima']")
        ))
        safe_click(driver, btn)

        # Página 2: Seleção da Rota
        time.sleep(2)
        dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@role='listbox']")))
        safe_click(driver, dropdown)
        time.sleep(1)
        opcao = wait.until(EC.element_to_be_clickable(
            (By.XPATH, f"//div[@role='option']//span[text()='{rota}']")
        ))
        safe_click(driver, opcao)
        time.sleep(1)
        btn2 = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//span[normalize-space(text())='Avançar' or normalize-space(text())='Próxima']")
        ))
        safe_click(driver, btn2)

        # Página 3: Telefone + Envio
        time.sleep(2)
        preencher_input(driver, wait, 0, telefone)
        btn_enviar = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//span[normalize-space(text())='Enviar']")
        ))
        safe_click(driver, btn_enviar)

        # Confirma sucesso
        wait.until(EC.presence_of_element_located(
            (By.XPATH, "//*[contains(text(), 'registrada') or contains(text(), 'agradecemos')]")
        ))
        log(f"Sucesso confirmado: {rota}", "OK")
        return True

    except Exception as e:
        log(f"Falha no envio de '{rota}': {e}", "ERRO")
        if tentativa < MAX_TENTATIVAS:
            log(f"Aguardando {INTERVALO_RETRY}s antes de retry...", "RETRY")
            time.sleep(INTERVALO_RETRY)
            if driver:
                driver.quit()
                driver = None
            return enviar_formulario(url, rota, nome, id_func, telefone, log, tentativa + 1)
        return False
    finally:
        if driver:
            driver.quit()

# ==================== INTERFACE STREAMLIT ====================

# ── Sidebar: Credenciais ──────────────────────────────────────
with st.sidebar:
    st.title("📋 Automação Forms")
    st.divider()

    st.subheader("👤 Dados do Funcionário")
    nome_input    = st.text_input("Nome completo", placeholder="Ex: João Silva",
                                   help="Preenchido no campo Nome do formulário")
    id_input      = st.text_input("ID do Funcionário", placeholder="Ex: 12345")
    telefone_input = st.text_input("Telefone", placeholder="Ex: 85999999999")

    st.divider()
    st.subheader("⚙️ Configurações Avançadas")

    with st.expander("Timeouts & Intervalos"):
        timeout_p   = st.number_input("Timeout padrão (s)", value=TIMEOUT_PADRAO, min_value=5)
        timeout_e   = st.number_input("Timeout envio (s)", value=TIMEOUT_ENVIO, min_value=5)
        intervalo   = st.number_input("Intervalo entre envios (s)", value=INTERVALO_ENTRE_ENVIOS, min_value=1)
        max_tent    = st.number_input("Máx. tentativas por rota", value=MAX_TENTATIVAS, min_value=1, max_value=5)

    st.divider()
    st.caption("Automação headless via Selenium · Chromium")

# ── Main ──────────────────────────────────────────────────────
st.title("📋 Automação Google Forms")
st.markdown("Preenche e envia formulários de escala automaticamente com base nos bairros configurados.")

# ── URL ───────────────────────────────────────────────────────
url_input = st.text_input(
    "🔗 URL do Formulário Google",
    placeholder="https://docs.google.com/forms/d/e/.../viewform",
    label_visibility="visible"
)

# ── Configuração de Bairros ───────────────────────────────────
with st.expander("🏘️ Configuração de Bairros", expanded=False):
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**Meus Bairros** *(um por linha)*")
        bairros_txt = st.text_area(
            "meus_bairros", label_visibility="hidden",
            value="\n".join(BAIRROS_DEFAULT), height=220,
            help="Bairros que você atende. O formulário será enviado apenas para rotas que contenham esses bairros."
        )
    with col_b:
        st.markdown("**Ordem de Preferência** *(um por linha)*")
        pref_txt = st.text_area(
            "bairros_pref", label_visibility="hidden",
            value="\n".join(BAIRROS_PREFERIDOS_DEFAULT), height=220,
            help="Bairros mais prioritários ficam no topo. Os demais ficam ao final da fila."
        )

meus_bairros   = [b.strip() for b in bairros_txt.splitlines() if b.strip()]
bairros_pref   = [b.strip() for b in pref_txt.splitlines() if b.strip()]

st.divider()

# ── Fase 1: Mapear Rotas ──────────────────────────────────────
col1, col2, col3 = st.columns([2, 2, 4])

with col1:
    btn_mapear = st.button("🗺️ Mapear Rotas", use_container_width=True, type="secondary")

with col2:
    btn_limpar = st.button("🔄 Limpar", use_container_width=True)

if btn_limpar:
    st.session_state.rotas_disponiveis = []
    st.session_state.rotas_selecionadas = []
    st.session_state.resultado = {}
    st.session_state.logs = []
    st.session_state.fase = "idle"
    st.rerun()

# Validações antes de mapear
if btn_mapear:
    erros = []
    if not nome_input.strip():    erros.append("Nome do funcionário")
    if not id_input.strip():      erros.append("ID do funcionário")
    if not telefone_input.strip(): erros.append("Telefone")
    if not url_input.strip():     erros.append("URL do formulário")
    elif not validar_url(url_input.strip()):
        erros.append("URL inválida (deve ser docs.google.com/forms ou forms.gle)")

    if erros:
        st.error("Preencha os campos obrigatórios: " + " · ".join(erros))
    else:
        st.session_state.logs = []
        st.session_state.rotas_disponiveis = []
        st.session_state.fase = "mapeando"

        log_placeholder = st.empty()
        log = make_log_fn(log_placeholder)

        with st.spinner("Mapeando rotas disponíveis no formulário..."):
            rotas = obter_rotas_disponiveis(
                url_input.strip(), nome_input.strip(),
                id_input.strip(), meus_bairros, log
            )

        if rotas:
            rotas_ord = ordenar_rotas_por_preferencia(rotas, bairros_pref)
            st.session_state.rotas_disponiveis = rotas_ord
            st.session_state.rotas_selecionadas = rotas_ord.copy()
            st.session_state.fase = "mapeado"
            st.rerun()
        else:
            st.session_state.fase = "idle"
            st.warning("Nenhuma rota compatível encontrada. Verifique a lista de bairros.")

# ── Exibir rotas mapeadas + seleção ───────────────────────────
if st.session_state.fase in ("mapeado", "concluido") and st.session_state.rotas_disponiveis:
    st.success(f"✅ {len(st.session_state.rotas_disponiveis)} rota(s) encontrada(s)")

    st.markdown("#### Selecione as rotas para envio:")
    selecionadas = []
    cols = st.columns(2)
    for i, rota in enumerate(st.session_state.rotas_disponiveis):
        status_icon = ""
        if rota in st.session_state.resultado:
            status_icon = " ✅" if st.session_state.resultado[rota] else " ❌"
        checked = st.session_state.resultado.get(rota) is None  # Desmarca as que já foram processadas
        with cols[i % 2]:
            if st.checkbox(rota + status_icon, value=checked, key=f"rota_{i}"):
                selecionadas.append(rota)

    st.session_state.rotas_selecionadas = selecionadas

    st.divider()

    # ── Fase 2: Enviar Formulários ────────────────────────────
    btn_enviar = st.button(
        f"🚀 Enviar {len(selecionadas)} Formulário(s)",
        type="primary", use_container_width=False,
        disabled=len(selecionadas) == 0
    )

    if btn_enviar:
        if not nome_input.strip() or not id_input.strip() or not telefone_input.strip():
            st.error("Credenciais incompletas na barra lateral.")
        else:
            st.session_state.logs = []
            st.session_state.resultado = {}
            st.session_state.fase = "enviando"

            log_placeholder = st.empty()
            log = make_log_fn(log_placeholder)

            progresso = st.progress(0, text="Iniciando envios...")
            total = len(selecionadas)
            sucesso_count, falha_count = 0, 0

            for idx, rota in enumerate(selecionadas, 1):
                progresso.progress(
                    (idx - 1) / total,
                    text=f"[{idx}/{total}] Enviando: {rota}"
                )
                log(f"[{idx}/{total}] Processando: {rota}", "PROC")

                ok = enviar_formulario(
                    url_input.strip(), rota,
                    nome_input.strip(), id_input.strip(), telefone_input.strip(),
                    log
                )
                st.session_state.resultado[rota] = ok

                if ok:
                    sucesso_count += 1
                else:
                    falha_count += 1

                if idx < total:
                    log(f"Aguardando {intervalo}s até próximo envio...", "WAIT")
                    time.sleep(intervalo)

            progresso.progress(1.0, text="Concluído!")
            st.session_state.fase = "concluido"

            # Resumo final
            st.divider()
            st.subheader("📊 Resumo Final")
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Enviado", total)
            c2.metric("✅ Sucessos", sucesso_count)
            c3.metric("❌ Falhas", falha_count)

            if falha_count == 0:
                st.success("Todos os formulários foram enviados com sucesso! 🎉")
            elif sucesso_count == 0:
                st.error("Nenhum formulário foi enviado com sucesso. Verifique os logs.")
            else:
                st.warning(f"{sucesso_count} enviado(s) com sucesso, {falha_count} com falha.")

# ── Log persistente (após execução) ──────────────────────────
if st.session_state.logs and st.session_state.fase not in ("enviando",):
    with st.expander("📄 Ver Logs da Última Execução", expanded=False):
        content = "\n".join(st.session_state.logs)
        st.markdown(f'<div class="log-box">{content}</div>', unsafe_allow_html=True)
        st.download_button(
            "⬇️ Baixar logs (.txt)",
            data="\n".join(st.session_state.logs),
            file_name="automacao_forms.log",
            mime="text/plain"
        )