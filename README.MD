# Análise de Sentimentos em Evolução de Software

## 📋 Tutorial da Atividade

O tutorial completo com as instruções passo a passo para realizar esta atividade está disponível em PDF:

[📖 **Acessar Tutorial em PDF**](./Douglas_Deda_Gabriel_Almeida_Henrick_Cardoso_Ian_Conceição_Mariana_Nunes_Pablo_Freire_Rafael_Oliveira_Yasmim_Lima_Atividade_1.pdf)

## 📰 Projeto
- [**ChatTTS**](https://github.com/2noise/ChatTTS)

## 🤖 Modelos

- [**Roberta**](https://huggingface.co/cardiffnlp/twitter-roberta-base-sentiment)
- [**Bertweet**](https://huggingface.co/finiteautomata/bertweet-base-sentiment-analysis)
- [**Multilingual**](https://huggingface.co/tabularisai/multilingual-sentiment-analysis)

## Estrutura do Projeto

    .
    ├── README.md
    ├── requirements.txt
    └── src
        ├── main.py
        ├── PRs_comments
        │   └── extract_pr_comments.py
        ├── models
        │   ├── BERTweet
        │   │   └── analise_bertweet.py
        │   ├── Multilingual
        │   │   └── analyzeMultilingual.py
        │   └── Roberta
        │       └── analyzeRobertaBase.py
        └── results
            ├── bertweet_sentiment_results.json
            ├── multilingual_sentiment_results.json
            └── roberta_sentiment_results.json
O arquivo pr_comments_2noise_ChatTTS_closed_nobots_True.json já contém os comentários dos PRs do ChatTTS que serão analisados pelos modelos.

## Pré-requisitos

Antes de rodar qualquer coisa, você vai precisar de:

- **Python 3.9+**
- **pip** (gerenciador de pacotes do Python)
- **Git** (para clonar o repositório)

## Fluxo resumido de execução
1. Clonar o repositório e instalar dependências.
2. Garantir que o arquivo `"src/PRs_comments/pr_comments_2noise_ChatTTS_closed_nobots_True.json"` está presente (já incluído no projeto).
3. Executar:
´´´bash
cd src
python main.py
´´´
4. Analisar os resultados em `"src/results/*.json."`
5. Coleta de comentários de PRs de outro repositório(opcional)


## 1. Instalação do Projeto

### 1.1. Clonar o repositório
```bash
    git clone https://github.com/faalkor/Evolucao_Software_2025-2_chatTTS.git
    cd Evolucao_Software_2025-2_chatTTS
```
### 1.2. Instalar dependências
```bash
    pip install -r requirements.txt
```

## 2. Como executar os modelos
Os comentários dos PRs já estão armazenados em:
```txt
src/PRs_comments/pr_comments_2noise_ChatTTS_closed_nobots_True.json
```
Os três modelos lêem esse arquivo automaticamente por meio da configuração:

```python
INPUT_FILE = os.path.join(
    BASE_DIR,
    '..',
    "PRs_comments",
    "pr_comments_2noise_ChatTTS_closed_nobots_True.json"
)
```

### 2.1. Execução unificada via main.py
O script `"src/main.py"` executa os três modelos em sequência:
```python
from models.BERTweet.analise_bertweet import run_bertweet
from models.Multilingual.analyzeMultilingual import run_multilingual
from models.Roberta.analyzeRobertaBase import run_roberta
```
Para rodar a análise completa:

```bash
cd src
python main.py
# ou python3 main.py
```

Na primeira execução, a biblioteca `"transformers"` irá baixar os modelos do Hugging Face.
Isso pode levar alguns minutos, dependendo da conexão.

Ao final, serão criados/atualizados os arquivos:
```text
src/results/bertweet_sentiment_results.json
src/results/multilingual_sentiment_results.json
src/results/roberta_sentiment_results.json
```
## 3. Formato dos arquivos de saída
Cada arquivo de resultados `"(*_sentiment_results.json)"` contém uma lista de objetos, um por comentário analisado.
Cada objeto tem a estrutura:
```json
{
  "pr_number": 123,
  "user": "login_do_usuario",
  "text": "conteúdo do comentário...",
  "label": "POSITIVE | NEUTRAL | NEGATIVE",
  "score": 0.987
}
```
- `"pr_number"`: número do pull request ao qual o comentário pertence
- `"user"`: autor do comentário
- `"text"`: texto do comentário (possivelmente truncado, ver seção 6)
- `"label"`: sentimento dominante atribuído pelo modelo
- `"score"`: confiança do modelo na classificação (probabilidade aproximada)

Além disso, cada script imprime no terminal um resumo com a contagem de comentários por classe de sentimento.

## 5. (Opcional) Coleta de comentários de PRs de outro repositório
Caso você queira reaplicar a pipeline de análise de sentimentos em qualquer outro repositório do GitHub, pode usar o script:
```text
src/PRs_comments/extract_pr_comments.py
```
Esse script:
- busca pull requests de um repositório específico;
- filtra bots;
- coleta comentários gerais e comentários de review;
- salva tudo em um único arquivo `".json."`

### 5.1. Requisitos extras

Para essa etapa opcional, é necessário:
- **Token de acesso pessoal do GitHub** com permissão de leitura em repositórios públicos(ou privados, se for analisar projetos privados da sua conta/org)
#### Como criar um token de acesso pessoal no GitHub (PAT)

1. Acesse: *Settings* > *Developer settings* > *Personal access tokens*.
2. Crie um novo token (fine-grained ou classic).
3. Dê permissão de leitura para:
   - `public_repo` (para repositórios públicos)  
   - e/ou permissões de leitura em repositórios privados, se necessário.
4. Copie o token gerado e guarde em local seguro.

### 5.2. Configurar o repositório a ser analisado

```text
src/PRs_comments/extract_pr_comments.py
```
No final do arquivo, dentro da função `"main()"`, localize:
```python
def main():
    # CONFIGURAÇÕES
    GITHUB_TOKEN = "seu_token"  # Token de acesso pessoal do GitHub
    REPO_OWNER = "owner_repositorio"  # Ex: "facebook"
    REPO_NAME = "nome_repositorio"  # Ex: "react"
```
Substitua:
- `""seu_token""` pelo seu token do GitHub;
- `""owner_repositorio""` pelo owner do repositório (usuário ou organização);
- `""nome_repositorio""` pelo nome do repositório.
Exemplo para o projeto ChatTTS oficial:
```python
GITHUB_TOKEN = "ghp_xxxSEUTOKENAQUIxxx"
REPO_OWNER = "2noise"
REPO_NAME = "ChatTTS"
```
### 5.3. Executar a coleta
No terminal, a partir da raiz do projeto:
```bash
cd src/PRs_comments
python extract_pr_comments.py
# ou python3 extract_pr_comments.py
```
O script:
1. Mostra o progresso dos PRs que estão sendo processados;
2. Cria um arquivo .json no mesmo diretório src/PRs_comments.
O nome do arquivo segue o padrão:
```text
pr_comments_<owner>_<repo>_<state>_nobots_<True/False>.json
```
Se quiser usar esse novo arquivo nos modelos, você pode:
- renomeá-lo para `"pr_comments_2noise_ChatTTS_closed_nobots_True.json"`, ou alterar o nome do arquivo em `"INPUT_FILE"` nos scripts:
1. `"src/models/BERTweet/analise_bertweet.py"`
2. `"src/models/Multilingual/analyzeMultilingual.py"`
3. `"src/models/Roberta/analyzeRobertaBase.py"`

Depois disso, basta repetir a execução da seção 2 E os modelos passarão a analisar os comentários do novo repositório escolhido.
