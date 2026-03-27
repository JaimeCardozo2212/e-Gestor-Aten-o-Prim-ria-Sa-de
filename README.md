🤖 Bot de Extração de Dados - Atenção Primária à Saúde (APS)
Este projeto é uma automação em Python utilizando Selenium para a extração assistida de relatórios de pagamento do portal oficial do governo. O robô navega pelos filtros de Estado e Município, acessa os detalhamentos de cada categoria e realiza o download automático de planilhas Excel, organizando-as em pastas específicas.

🚀 Funcionalidades
Filtros Dinâmicos: Seleção automática de Estado, Município, Ano e Competência.

Navegação em Abas: Gerenciamento inteligente de múltiplas janelas para acessar detalhes de pagamentos.

Organização Automática: Criação de pastas baseadas no nome do Município para salvar os arquivos.

Limpeza Inteligente: Verificação automática de arquivos baixados (apaga planilhas que contêm apenas cabeçalho e nenhum dado).

Modo Headless: Opção de rodar sem interface gráfica (em segundo plano).

Logs Detalhados: Registro de todas as ações e erros em um arquivo execucao_bot.log.

🛠️ Pré-requisitos
Antes de começar, você precisará ter instalado:

Python 3.10+

Google Chrome (Versão atualizada)

ChromeDriver (O Selenium geralmente gerencia isso sozinho nas versões recentes)

📦 Instalação
Clone o repositório ou baixe os arquivos:

Bash
git clone https://github.com/seu-usuario/seu-projeto.git
cd seu-projeto
Instale as bibliotecas necessárias:

Bash
pip install selenium pandas openpyxl requests
⚙️ Configuração
No início do script main.py, você pode ajustar as variáveis de busca:

Python
ESTADO_BUSCA = "SANTA CATARINA"
MUNICIPIO_BUSCA = "JOINVILLE"
ANO_BUSCA = "2026"
PARCELA_BUSCA = "Janeiro"
🖥️ Como usar
Para rodar a automação, execute o comando:

Bash
python main.py
O robô irá:

Abrir o navegador (ou rodar em background se o modo headless estiver ativo).

Aplicar os filtros no portal.

Criar a pasta downloads/ESTADO/MUNICIPIO.

Baixar e validar cada planilha encontrada.

📂 Estrutura de Arquivos
main.py: O script principal da automação.

downloads/: Pasta raiz onde os dados serão organizados.

execucao_bot.log: Arquivo gerado automaticamente com o histórico de execuções.

README.md: Este arquivo de documentação.

⚠️ Observações Importantes
Tempo de Carregamento: O site do governo pode ser instável. O script possui pausas (time.sleep) estratégicas para garantir a sincronização.

IDs Dinâmicos: O portal utiliza o framework PrimeNG, o que significa que alguns IDs de botões podem mudar. O script utiliza seletores baseados em texto para maior estabilidade.
