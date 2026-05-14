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


def normalizar_texto(texto: str) -> str:
    """Normaliza espaços extras para comparação estável."""
    return " ".join((texto or "").split()).strip()

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


async def ir_para_pagina_rotas(page) -> bool:
    """Avança para a página de rotas com fallback de seletores."""
    # Verificar se já está na página de rotas
    if await page.locator("[role='listbox']").count() > 0:
        return True

    # Tentar clicar em botão de avanço (com XPath simples e direto)
    try:
        btn_avancar = await page.query_selector("//span[contains(text(), 'Avançar') or contains(text(), 'Próxima') or contains(text(), 'Next')]/ancestor::button[1]")
        if btn_avancar:
            await btn_avancar.click(timeout=5000)
    except:
        # Se não achou por XPath, tentar via evaluate
        await page.evaluate("""() => {
            const btn = Array.from(document.querySelectorAll('button')).find(b => 
                b.textContent.includes('Avançar') || b.textContent.includes('Próxima') || b.textContent.includes('Next')
            );
            if (btn) btn.click();
        }""")

    # Aguardar a página de rotas carregar (max 15s)
    for _ in range(30):
        if await page.locator("[role='listbox']").count() > 0:
            await page.wait_for_timeout(1000)
            return True
        await page.wait_for_timeout(500)

    return False

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
            inputs_locator = page.locator("input[type='text'], input[type='tel'], input[type='number']")
            count_inputs = await inputs_locator.count()
            if count_inputs < 2:
                progress_placeholder.error(f"❌ Não foi possível localizar os 2 campos de identificação (encontrados: {count_inputs})")
                return []
            await inputs_locator.nth(0).fill(NOME)
            await inputs_locator.nth(1).fill(ID_FUNC)
            
            # Clicar em Avançar
            progress_placeholder.info("⬜ Avançando para próxima página...")
            avancou = await ir_para_pagina_rotas(page)
            if not avancou:
                # Diagnóstico detalhado para entender DOM no ambiente
                info_lines = []
                try:
                    count_listbox = await page.locator("[role='listbox']").count()
                    count_select = await page.locator("select").count()
                    count_options = await page.locator("[role='option']").count()
                    count_buttons = await page.locator("button").count()
                    info_lines.append(f"listbox: {count_listbox}")
                    info_lines.append(f"select: {count_select}")
                    info_lines.append(f"options(role=option): {count_options}")
                    info_lines.append(f"buttons: {count_buttons}")

                    # coletar textos dos primeiros botões
                    btns = page.locator("button")
                    sample_btns = min(8, await btns.count())
                    for i in range(sample_btns):
                        txt = (await btns.nth(i).inner_text()) or ""
                        info_lines.append(f"btn[{i}]: {txt.strip()}")

                    # mostrar trecho do primeiro listbox/html
                    lb = await page.query_selector("[role='listbox']")
                    if lb:
                        outer = await lb.evaluate("el => el.outerHTML.slice(0,400)")
                        info_lines.append(f"listbox_html: {outer}")
                except Exception as e:
                    info_lines.append(f"diagnostic_error: {str(e)}")

                progress_placeholder.error("❌ Não foi possível avançar para a página de rotas")
                for line in info_lines:
                    progress_placeholder.code(line)
                return []
            
            # Página 2: Abrir dropdown
            progress_placeholder.info("🔍 Extraindo rotas disponíveis...")
            dropdown = await page.query_selector("//*[@role='listbox'] | //select")
            if dropdown:
                await dropdown.click()
                await page.wait_for_timeout(1000)
            await page.wait_for_selector("//*[@role='option'] | //select/option", timeout=10000)
            
            # Extrair opções
            opcoes = await page.query_selector_all("//*[@role='listbox']//*[@role='option'] | //*[@role='option'] | //select/option")
            rotas = []
            rotas_unicas = set()
            
            meus_bairros_limpos = [remover_acentos(b) for b in MEUS_BAIRROS]
            
            for opcao in opcoes:
                texto_attr = await opcao.get_attribute("data-value")
                texto_inner = await opcao.inner_text()
                texto_normalizado = normalizar_texto(texto_attr or texto_inner)
                if texto_normalizado and remover_acentos(texto_normalizado) != "escolher":
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
            inputs_locator = page.locator("input[type='text'], input[type='tel'], input[type='number']")
            count_inputs = await inputs_locator.count()
            if count_inputs < 2:
                progress_placeholder.error(f"❌ [{index}/{total}] Campos de identificação não encontrados (encontrados: {count_inputs})")
                return False
            await inputs_locator.nth(0).fill(NOME)
            await inputs_locator.nth(1).fill(ID_FUNC)
            
            avancou = await ir_para_pagina_rotas(page)
            if not avancou:
                progress_placeholder.error(f"❌ [{index}/{total}] Não foi possível acessar a página de rotas")
                return False
            
            # Página 2: Selecionar rota
            dropdown = await page.query_selector("//*[@role='listbox'] | //select")
            if dropdown:
                await dropdown.click()
                await page.wait_for_timeout(1000)
            await page.wait_for_selector("//*[@role='option'] | //select/option", timeout=10000)
            
            # Encontrar e clicar na rota pelo texto (role='option' dentro de listbox)
            rota_limpa = remover_acentos(rota)
            opcoes = await page.query_selector_all("[role='option']")
            opcao_encontrada = None
            
            for op in opcoes:
                texto_inner = await op.inner_text()
                if texto_inner and remover_acentos(texto_inner.strip()) == rota_limpa:
                    opcao_encontrada = op
                    break
            
            if not opcao_encontrada:
                progress_placeholder.warning(f"⚠️ [{index}/{total}] Rota '{rota}' não localizada nas opções disponíveis")
                return False
            
            # Clicar na opção encontrada via JS para evitar interceptação de eventos
            try:
                await opcao_encontrada.evaluate("el => el.click()")
            except:
                # fallback: usar scroll + click normal
                await opcao_encontrada.scroll_into_view_if_needed()
                try:
                    await opcao_encontrada.click(timeout=5000)
                except:
                    progress_placeholder.warning(f"⚠️ [{index}/{total}] Não foi possível clicar na rota '{rota}'")
                    return False
            
            await page.wait_for_timeout(1500)
            
            # Avançar
            avancar_btn2 = await page.query_selector("//span[normalize-space(text())='Avançar' or normalize-space(text())='Próxima']")
            if avancar_btn2:
                await avancar_btn2.click()
            await page.wait_for_timeout(2000)
            
            # Página 3: Telefone
            # Usar aria-label específico que aparece no formulário: "Número de telefone com DDD"
            phone_input = page.locator("[aria-label*='elefone']").first
            try:
                await phone_input.fill(TELEFONE, timeout=5000)
            except:
                progress_placeholder.error(f"❌ [{index}/{total}] Campo de telefone não encontrado")
                return False
            
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
