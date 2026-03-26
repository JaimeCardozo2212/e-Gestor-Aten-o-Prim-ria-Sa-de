import os
import time
import logging
import pandas as pd
import glob
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- 1. CONFIGURAÇÃO DE LOGS ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("execucao_bot.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
# --- FILTROS DINÂMICOS ---
ESTADO_BUSCA = "SANTA CATARINA"
MUNICIPIO_BUSCA = "FLORIANÓPOLIS"
ANO_BUSCA = "2026"
PARCELA_BUSCA = "3/12" # Use o nome conforme aparece no site

# --- 2. CONFIGURAÇÕES INICIAIS ---
pasta_download = os.path.join(os.getcwd(), "downloads")
if not os.path.exists(pasta_download):
    os.makedirs(pasta_download)
pasta_base = os.path.join(os.getcwd(), "downloads")
pasta_final = os.path.join(pasta_base, ESTADO_BUSCA, MUNICIPIO_BUSCA.replace(" ", "_"))

if not os.path.exists(pasta_final):
    os.makedirs(pasta_final)
    print(f"📂 Pasta criada: {pasta_final}")

chrome_options = Options()
prefs = {
    "download.default_directory": pasta_final,
    "download.prompt_for_download": False,
    "profile.default_content_setting_values.automatic_downloads": 1 
    
}
chrome_options.add_experimental_option("prefs", prefs)
chrome_options.add_argument("--headless") # Roda sem abrir a janela
chrome_options.add_argument("--disable-gpu") # Recomendado para evitar bugs em modo headless
chrome_options.add_argument("--window-size=1920,1080") # Define um tamanho fixo para não quebrar o layout

driver = webdriver.Chrome(options=chrome_options)
# driver.maximize_window()
wait = WebDriverWait(driver, 15)
wait_download = WebDriverWait(driver, 5) # Para esperar os downloads aparecerem

contador_sucesso = 0

# --- 3. FUNÇÕES AUXILIARES ---
def selecionar_opcao_por_texto(id_dropdown, texto_opcao):
    """Abre um dropdown e clica na opção que contém o texto especificado."""
    try:
        # 1. Clica no dropdown para abrir as opções
        drop = wait.until(EC.element_to_be_clickable((By.ID, id_dropdown)))
        driver.execute_script("arguments[0].click();", drop)
        time.sleep(1) # Espera as opções aparecerem
        
        # 2. Busca a opção que contém o texto exato dentro do painel que abriu
        # O PrimeNG costuma colocar as opções em <li> ou <span>
        xpath_opcao = f"//li[contains(@class, 'p-dropdown-item')]//span[contains(text(), '{texto_opcao}')]"
        
        # Caso o span não funcione, tentamos o li direto
        try:
            opcao = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_opcao)))
        except:
            xpath_opcao = f"//li[contains(text(), '{texto_opcao}')]"
            opcao = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_opcao)))
            
        driver.execute_script("arguments[0].click();", opcao)
        logging.info(f"Selecionado: {texto_opcao}")
        time.sleep(1)
    except Exception as e:
        logging.error(f"Erro ao selecionar {texto_opcao}: {e}")
        raise

def validar_e_limpar_ultimo_download(pasta):
    """Verifica se o último arquivo baixado tem conteúdo."""
    time.sleep(3) # Tempo para o SO processar o arquivo
    arquivos = glob.glob(os.path.join(pasta, "*.xlsx"))
    if not arquivos: return False
    
    ultimo_arquivo = max(arquivos, key=os.path.getctime)
    try:
        df = pd.read_excel(ultimo_arquivo)
        if df.empty or len(df) == 0:
            logging.warning(f"Arquivo vazio apagado: {os.path.basename(ultimo_arquivo)}")
            os.remove(ultimo_arquivo)
            return False
        logging.info(f"Arquivo válido: {os.path.basename(ultimo_arquivo)} ({len(df)} linhas)")
        return True
    except Exception as e:
        logging.error(f"Erro ao validar {ultimo_arquivo}: {e}")
        return False

def localizar_e_clicar(xpath, descricao):
    """Tenta clicar em um elemento com tratamento de erro."""
    try:
        elemento = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
        elemento.click()
        logging.info(f"Clicou em: {descricao}")
    except Exception as e:
        logging.error(f"Falha ao clicar em {descricao}: {e}")
        raise # Repassa o erro para o bloco principal

# --- 4. EXECUÇÃO ---

try:
    driver.get("https://relatorioaps.saude.gov.br/gerenciaaps/pagamento")
    logging.info("Site acessado.")

    # Etapa de Filtros (Usei seus XPaths, mas com a função nova)
    localizar_e_clicar('//*[@id="tipo-unidade"]', "Dropdown Unidade")
    localizar_e_clicar('//*[@id="pn_id_3_1"]', "Opção Município")
    # localizar_e_clicar('//*[@id="pn_id_5"]/div', "Dropdown Estado")
    selecionar_opcao_por_texto("pn_id_5", ESTADO_BUSCA)
    # localizar_e_clicar('//*[@id="pn_id_15"]/div', "Dropdown Município")
    selecionar_opcao_por_texto("pn_id_15", MUNICIPIO_BUSCA)
    # localizar_e_clicar('//*[@id="pn_id_7"]/div', "Ano")
    selecionar_opcao_por_texto("pn_id_7", ANO_BUSCA)
    # localizar_e_clicar('//*[@id="pn_id_9"]/div', "Parcela Início")
    selecionar_opcao_por_texto("pn_id_9", PARCELA_BUSCA)
    # localizar_e_clicar('//*[@id="pn_id_11"]/div', "Parcela Fim")
    selecionar_opcao_por_texto("pn_id_11", PARCELA_BUSCA)
    localizar_e_clicar('//*[@id="main-content"]/app-relatorio-pagamento-financiamento/div[2]/app-formulario-pagamento-financiamento/form/div[2]/app-botao-download-excel/app-botao/button', "Botão Download")
    localizar_e_clicar('//*[@id="main-content"]/app-relatorio-pagamento-financiamento/div[2]/app-formulario-pagamento-financiamento/form/div[2]/app-botao/button', "Botão Pesquisar")

    # Esperar tabela carregar
    time.sleep(3)
    # localizar_elemento('//*[@id="pn_id_18-table"]/tbody/tr/td[1]/p-button/button')
    botao_proximo = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[span[contains(@class, 'pi-chevron-right')]]")))
    botao_proximo.click()
    time.sleep(2)

    aba_principal = driver.current_window_handle

    # Localizar botões da tabela
    botoes = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//tbody/tr//button[contains(@class, 'p-button-icon-only')]")))
    logging.info(f"Total de linhas encontradas: {len(botoes)}")

    for i in range(1, len(botoes)):
        try:
            # Re-localizar para evitar StaleElement
            botoes_at = driver.find_elements(By.XPATH, "//tbody/tr//button[contains(@class, 'p-button-icon-only')]")
            if i >= len(botoes_at): break
            
            btn_seta = botoes_at[i]
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn_seta)
            driver.execute_script("arguments[0].click();", btn_seta)
            logging.info(f"Processando linha {i+1}...")
            time.sleep(2)

            # Botões de Detalhes
            detalhes = driver.find_elements(By.XPATH, "//button[span[contains(text(), 'Ver Detalhes')]]")
            
            for idx, btn_det in enumerate(detalhes):
                try:
                    # Clicar no detalhe (re-localizando se necessário)
                    detalhes_at = driver.find_elements(By.XPATH, "//button[span[contains(text(), 'Ver Detalhes')]]")
                    driver.execute_script("arguments[0].click();", detalhes_at[idx])
                    
                    # Troca de aba
                    wait.until(lambda d: len(d.window_handles) > 1)
                    nova_aba = [w for w in driver.window_handles if w != aba_principal][0]
                    driver.switch_to.window(nova_aba)

                    # Downloads
                    wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(@id, 'main-content')]//app-tela-detalhamento//app-quadro-detalhamento//app-item-detalhamento[1]/div")))
                    time.sleep(0.5) # Pequena pausa para garantir que os botões de download estejam interativos
                    btns_dw = driver.find_elements(By.XPATH, "//button[contains(@aria-label, 'Download')]")
                    
                    for d_btn in btns_dw:
                        driver.execute_script("arguments[0].click();", d_btn)
                        time.sleep(0.6) # Espera o download iniciar
                        if validar_e_limpar_ultimo_download(pasta_final):
                            contador_sucesso += 1
                    
                    driver.close()
                    driver.switch_to.window(aba_principal)
                except Exception as e_interna:
                    logging.error(f"Erro no detalhe {idx} da linha {i+1}: {e_interna}")
                    driver.save_screenshot("erro_captura.png")
                    # Garante que volta para a aba principal se algo der errado
                    if len(driver.window_handles) > 1:
                        driver.close()
                    driver.switch_to.window(aba_principal)

            # Fechar Dropdown
            driver.execute_script("arguments[0].click();", btn_seta)
            time.sleep(1)

        except Exception as e_linha:
            logging.error(f"Erro crítico na linha {i+1}: {e_linha}")
            driver.save_screenshot("erro_captura.png")
            continue # Pula para a próxima linha da tabela principal

    logging.info(f"AUTOMAÇÃO FINALIZADA. Arquivos válidos baixados: {contador_sucesso}")

except Exception as e_geral:
    logging.critical(f"A automação parou por um erro inesperado: {e_geral}")
    driver.save_screenshot("erro_captura.png")

finally:
    driver.quit()