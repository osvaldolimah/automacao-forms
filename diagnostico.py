#!/usr/bin/env python3
"""
Script de diagnóstico para verificar se o ambiente está pronto para rodar a automação.
Útil para debugar problemas de deployment no Streamlit Cloud.
"""

import os
import sys
import subprocess
from pathlib import Path

print("=" * 70)
print("🔍 DIAGNÓSTICO DE AMBIENTE - Automação Google Forms")
print("=" * 70)

# 1. Verificar Python
print("\n1️⃣  Python")
print(f"   Versão: {sys.version}")
print(f"   Executável: {sys.executable}")

# 2. Verificar pacotes Python essenciais
print("\n2️⃣  Pacotes Python")
pacotes = ["streamlit", "selenium", "webdriver_manager"]
for pkg in pacotes:
    try:
        __import__(pkg)
        print(f"   ✅ {pkg}")
    except ImportError:
        print(f"   ❌ {pkg} - NÃO ENCONTRADO")

# 3. Verificar Chrome/Chromium
print("\n3️⃣  Chrome/Chromium")
CHROME_BINARIES = [
    "/usr/bin/chromium-browser",
    "/usr/bin/chromium",
    "/usr/bin/google-chrome",
    "/usr/bin/google-chrome-stable",
    "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",  # Windows
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",  # macOS
]

chrome_found = False
for path in CHROME_BINARIES:
    if os.path.exists(path):
        print(f"   ✅ Encontrado: {path}")
        chrome_found = True
        # Tentar pegar versão
        try:
            result = subprocess.run([path, "--version"], capture_output=True, text=True, timeout=5)
            print(f"      Versão: {result.stdout.strip()}")
        except:
            pass

if not chrome_found:
    print(f"   ❌ Chrome/Chromium NÃO ENCONTRADO")
    print(f"      Caminhos verificados: {len(CHROME_BINARIES)}")

# 4. Verificar ChromeDriver
print("\n4️⃣  ChromeDriver")
CHROMEDRIVER_PATHS = [
    "/usr/bin/chromedriver",
    "/usr/local/bin/chromedriver",
    "C:\\chromedriver.exe",
]

driver_found = False
for path in CHROMEDRIVER_PATHS:
    if os.path.exists(path):
        print(f"   ✅ Encontrado: {path}")
        driver_found = True
        try:
            result = subprocess.run([path, "--version"], capture_output=True, text=True, timeout=5)
            print(f"      Versão: {result.stdout.strip()}")
        except:
            pass

if not driver_found:
    print(f"   ❌ ChromeDriver NÃO ENCONTRADO (tentaremos webdriver-manager)")

# 5. Verificar ambiente
print("\n5️⃣  Ambiente")
if os.path.exists("/.dockerenv") or os.path.exists("/.streamlit"):
    print("   🐳 Detectado: Container/Streamlit Cloud")
elif "GOOGLE_APPLICATION_CREDENTIALS" in os.environ:
    print("   ☁️  Detectado: Google Cloud")
elif "HEROKU_APP_NAME" in os.environ:
    print("   ⚙️  Detectado: Heroku")
else:
    print("   💻 Detectado: Ambiente Local")

# 6. Verificar Selenium
print("\n6️⃣  Selenium WebDriver")
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    
    print("   ✅ Selenium importado com sucesso")
    
    # Tentar criar um driver (sem abrir navegador)
    try:
        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        if chrome_found:
            driver = webdriver.Chrome(options=options)
        else:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
        
        print("   ✅ ChromeDriver criado com sucesso!")
        print(f"      User-Agent: {driver.execute_script('return navigator.userAgent;')}")
        driver.quit()
    except Exception as e:
        print(f"   ❌ Erro ao criar ChromeDriver: {e}")
        
except Exception as e:
    print(f"   ❌ Erro ao importar Selenium: {e}")

# 7. Verificar arquivos de configuração
print("\n7️⃣  Arquivos de Configuração")
config_files = [
    "requirements.txt",
    "packages.txt",
    ".streamlit/config.toml",
    "app.py"
]

for file in config_files:
    if os.path.exists(file):
        size = os.path.getsize(file)
        print(f"   ✅ {file} ({size} bytes)")
    else:
        print(f"   ❌ {file} - FALTANDO")

# Resumo final
print("\n" + "=" * 70)
print("📊 RESUMO")
print("=" * 70)

if chrome_found and (driver_found or "selenium" in sys.modules):
    print("✅ Ambiente parece estar OK para rodar a automação!")
elif chrome_found:
    print("⚠️  Chrome encontrado, mas talvez hajam problemas com ChromeDriver")
    print("   Tentando usar webdriver-manager como fallback...")
else:
    print("❌ Chrome/Chromium NÃO ENCONTRADO")
    print("\n💡 Soluções:")
    print("   - Se está no Streamlit Cloud: atualize packages.txt e redeploy")
    print("   - Se está localmente: instale Chrome/Chromium")
    print("   - Verifique a documentação em DEPLOY.md")

print("\n" + "=" * 70)
