"""
Streamlit App para automação de formulários Google
Usa Playwright para melhor suporte em servidor
"""

import streamlit as st
import asyncio
import unicodedata
import os
import subprocess
import sys
from pathlib import Path
from typing import List
from urllib.parse import urlparse
from dotenv import load_dotenv

# Importar playwright
from playwright.async_api import async_playwright

if os.name == "nt":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


@st.cache_resource(show_spinner=False)
def garantir_chromium_playwright() -> None:
    """Garante que o Chromium do Playwright esteja disponível no ambiente."""
    browsers_path = Path(os.getenv("PLAYWRIGHT_BROWSERS_PATH", str(Path.home() / ".cache" / "ms-playwright")))
    if any(browsers_path.glob("chromium-*")):
        return

    subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)


def executar_corrotina(corrotina):
    """Executa corrotinas usando loop Proactor no Windows para suportar subprocessos."""
    if os.name == "nt":
        loop = asyncio.ProactorEventLoop()
        try:
            asyncio.set_event_loop(loop)
            return loop.run_until_complete(corrotina)
        finally:
            loop.close()
    return asyncio.run(corrotina)

# ==================== CONFIGURAÇÃO ====================
st.set_page_config(page_title="Automação Forms", layout="centered", initial_sidebar_state="collapsed")

# Carregar variáveis de ambiente
load_dotenv()

NOME = os.getenv("NOME_FUNCIONARIO", "").strip()
ID_FUNC = os.getenv("ID_FUNCIONARIO", "").strip()
TELEFONE = os.getenv("TELEFONE", "").strip()

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

# ==================== FUNÇÕES ====================

def remover_acentos(texto: str) -> str:
    """Remove acentos do texto."""
    nfd = unicodedata.normalize('NFD', texto)
    return ''.join(c for c in nfd if unicodedata.category(c) != 'Mn').lower()

def validar_url(url: str) -> bool:
    """Valida URL do formulário Google."""
    try:
        resultado = urlparse(url)
        return resultado.scheme in ('http', 'https') and ('forms.google.com' in resultado.netloc or 'docs.google.com' in resultado.netloc)
    except:
        return False

def ordenar_rotas_por_preferencia(rotas: List[str]) -> List[str]:
    """Reordena rotas por preferência."""
    rotas_preferidas = []
    rotas_restantes = []
    
    bairros_pref_normalizados = {remover_acentos(b): b for b in BAIRROS_PREFERIDOS}
    
    for rota in rotas:
        rota_normalizada = remover_acentos(rota)
        encontrou_preferido = False
        for bairro_pref_norm, bairro_pref_original in bairros_pref_normalizados.items():
            if bairro_pref_norm in rota_normalizada:
                rotas_preferidas.append((BAIRROS_PREFERIDOS.index(bairro_pref_original), rota))
                encontrou_preferido = True
                break
        
        if not encontrou_preferido:
            rotas_restantes.append(rota)
    
    rotas_preferidas.sort(key=lambda x: x[0])
    return [rota for _, rota in rotas_preferidas] + rotas_restantes


def _playwright_launch_args() -> dict:
    """Argumentos estáveis para rodar Chromium em ambiente de container/cloud."""
    return {
        "headless": True,
        "args": [
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
        ],
    }

async def obter_rotas_disponiveis(url: str, progress_placeholder):
    """Extrai rotas disponíveis do formulário."""
    garantir_chromium_playwright()

    async with async_playwright() as p:
        browser = None
        
        try:
            browser = await p.chromium.launch(**_playwright_launch_args())
            page = await browser.new_page()

            progress_placeholder.info("📄 Abrindo formulário...")
            await page.goto(url, wait_until="networkidle")
            
            # Página 1: Preencher nome e ID
            progress_placeholder.info("✍️ Preenchendo identificação...")
            inputs = await page.query_selector_all("input[type='text']")
            await inputs[0].fill(NOME)
            await inputs[1].fill(ID_FUNC)
            
            # Clicar em Avançar
            progress_placeholder.info("⬜ Avançando para próxima página...")
            avancar_btn = await page.query_selector("//span[normalize-space(text())='Avançar' or normalize-space(text())='Próxima']")
            if avancar_btn:
                await avancar_btn.click()
            await page.wait_for_timeout(2500)
            await page.wait_for_selector("//*[@role='listbox']", timeout=20000)
            
            # Página 2: Abrir dropdown
            progress_placeholder.info("🔍 Extraindo rotas disponíveis...")
            dropdown = await page.query_selector("//*[@role='listbox']")
            if dropdown:
                await dropdown.click()
                await page.wait_for_timeout(1000)
            
            # Extrair opções
            opcoes = await page.query_selector_all("//*[@role='listbox']//*[@role='option'] | //*[@role='option'] | //select/option")
            rotas = []
            rotas_unicas = set()
            
            meus_bairros_limpos = [remover_acentos(b) for b in MEUS_BAIRROS]
            
            for opcao in opcoes:
                texto = await opcao.inner_text()
                if texto and texto.strip().lower() != "escolher":
                    texto_normalizado = " ".join(texto.split()).strip()
                    texto_limpo = remover_acentos(texto_normalizado)
                    if any(b_limpo in texto_limpo for b_limpo in meus_bairros_limpos):
                        if texto_limpo not in rotas_unicas:
                            rotas_unicas.add(texto_limpo)
                            rotas.append(texto_normalizado)
            
            progress_placeholder.success(f"✅ {len(rotas)} rotas encontradas!")
            return rotas
        
        except Exception as e:
            progress_placeholder.error(f"❌ Erro ao extrair rotas: {str(e)}")
            return []
        
        finally:
            if browser:
                await browser.close()

async def enviar_formulario(url: str, rota: str, progress_placeholder, index: int, total: int) -> bool:
    """Envia o formulário para uma rota específica."""
    garantir_chromium_playwright()

    async with async_playwright() as p:
        browser = None
        
        try:
            browser = await p.chromium.launch(**_playwright_launch_args())
            page = await browser.new_page()

            progress_placeholder.info(f"📨 [{index}/{total}] Enviando: {rota}...")
            await page.goto(url, wait_until="networkidle")
            
            # Página 1
            inputs = await page.query_selector_all("input[type='text']")
            await inputs[0].fill(NOME)
            await inputs[1].fill(ID_FUNC)
            
            avancar_btn = await page.query_selector("//span[normalize-space(text())='Avançar' or normalize-space(text())='Próxima']")
            if avancar_btn:
                await avancar_btn.click()
            await page.wait_for_timeout(2500)
            await page.wait_for_selector("//*[@role='listbox']", timeout=20000)
            
            # Página 2: Selecionar rota
            dropdown = await page.query_selector("//*[@role='listbox']")
            if dropdown:
                await dropdown.click()
                await page.wait_for_timeout(1000)
            
            opcao = None
            opcoes = await page.query_selector_all("//*[@role='listbox']//*[@role='option'] | //*[@role='option'] | //select/option")
            rota_limpa = remover_acentos(rota)
            for op in opcoes:
                texto_opcao = (await op.inner_text()).strip()
                if remover_acentos(texto_opcao) == rota_limpa:
                    opcao = op
                    break
            if not opcao:
                for op in opcoes:
                    texto_opcao = (await op.inner_text()).strip()
                    if rota_limpa in remover_acentos(texto_opcao):
                        opcao = op
                        break
            if opcao:
                await opcao.click()
            await page.wait_for_timeout(1000)
            
            # Avançar
            avancar_btn2 = await page.query_selector("//span[normalize-space(text())='Avançar' or normalize-space(text())='Próxima']")
            if avancar_btn2:
                await avancar_btn2.click()
            await page.wait_for_timeout(2000)
            
            # Página 3: Telefone
            inputs = await page.query_selector_all("input[type='text']")
            await inputs[0].fill(TELEFONE)
            
            # Enviar
            enviar_btn = await page.query_selector("//span[normalize-space(text())='Enviar']")
            if enviar_btn:
                await enviar_btn.click()
            
            await page.wait_for_timeout(3000)
            
            # Verificar sucesso
            try:
                await page.wait_for_selector("//*[contains(text(), 'registrada') or contains(text(), 'agradecemos')]", timeout=5000)
                progress_placeholder.success(f"✅ [{index}/{total}] {rota} enviado com sucesso!")
                return True
            except:
                progress_placeholder.warning(f"⚠️ [{index}/{total}] {rota} - status incerto")
                return False
        
        except Exception as e:
            progress_placeholder.error(f"❌ [{index}/{total}] Erro em {rota}: {str(e)}")
            return False
        
        finally:
            if browser:
                await browser.close()

# ==================== UI ====================

st.title("🚀 Automação Forms")
st.markdown("Execute seus formulários Google automaticamente")

# Verificar se credenciais estão configuradas
if not all([NOME, ID_FUNC, TELEFONE]):
    st.error("❌ Credenciais não configuradas. Configure as variáveis de ambiente:")
    st.code("NOME_FUNCIONARIO=Seu Nome\nID_FUNCIONARIO=123456\nTELEFONE=85988449973")
    st.stop()

# Input da URL
st.markdown("---")
url = st.text_input(
    "📋 Cole a URL do formulário Google:",
    placeholder="https://forms.gle/... ou https://docs.google.com/forms/..."
)

# Botões
col1, col2 = st.columns(2)
with col1:
    executar = st.button("▶️ Executar Automação", use_container_width=True)
with col2:
    limpar = st.button("🗑️ Limpar", use_container_width=True)

if limpar:
    st.rerun()

# Executar automação
if executar:
    if not url:
        st.error("❌ Cole a URL do formulário primeiro!")
        st.stop()
    
    if not validar_url(url):
        st.error("❌ URL inválida! Use um formulário Google válido.")
        st.stop()
    
    progress_container = st.container()
    progress_placeholder = progress_container.empty()
    
    # Obter rotas
    progress_placeholder.info("🔍 Extraindo rotas disponíveis...")
    rotas = executar_corrotina(obter_rotas_disponiveis(url, progress_placeholder))
    
    if not rotas:
        st.error("❌ Nenhuma rota compatível encontrada no formulário")
        st.stop()
    
    # Reordenar
    rotas_ordenadas = ordenar_rotas_por_preferencia(rotas)
    
    # Enviar cada rota
    st.markdown("---")
    st.markdown(f"### 📊 Enviando {len(rotas_ordenadas)} rota(s)...")
    
    resultados = []
    sucessos = 0
    falhas = 0
    
    for idx, rota in enumerate(rotas_ordenadas, 1):
        progress_placeholder = st.empty()
        sucesso = executar_corrotina(enviar_formulario(url, rota, progress_placeholder, idx, len(rotas_ordenadas)))
        
        resultados.append({
            'rota': rota,
            'sucesso': sucesso,
            'icon': '✅' if sucesso else '❌'
        })
        
        if sucesso:
            sucessos += 1
        else:
            falhas += 1
    
    # Resumo
    st.markdown("---")
    total = len(rotas_ordenadas)
    percentual = round((sucessos / total * 100) if total > 0 else 0, 1)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total", total)
    with col2:
        st.metric("Sucesso", sucessos)
    with col3:
        st.metric("Falha", falhas)
    with col4:
        st.metric("Taxa", f"{percentual}%")
    
    # Detalhes
    st.markdown("### 📋 Detalhes das rotas:")
    for resultado in resultados:
        st.write(f"{resultado['icon']} {resultado['rota']}")
    
    st.success(f"✅ Automação concluída! {sucessos}/{total} rotas enviadas com sucesso.")
