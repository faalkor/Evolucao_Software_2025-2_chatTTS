import requests
import json
import time
import sys
import os
from typing import List, Dict, Any

# Configurar encoding para UTF-8 no Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

class GitHubPRComments:
    def __init__(self, token: str, owner: str, repo: str):
        self.token = token
        self.owner = owner
        self.repo = repo
        self.base_url = f"https://api.github.com/repos/{owner}/{repo}"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    def safe_print(self, message: str):
        """Print seguro para caracteres Unicode"""
        try:
            print(message)
        except UnicodeEncodeError:
            # Remove ou substitui caracteres problemáticos
            safe_message = message.encode('utf-8', errors='ignore').decode('utf-8')
            print(safe_message)
    
    def is_bot_user(self, user_login: str) -> bool:
        """Verifica se o usuário é um bot"""
        bot_indicators = [
            'bot', 'github-actions', 'actions', 'dependabot', 
            'renovate', 'automatic', 'ci', 'travis', 'jenkins'
        ]
        user_lower = user_login.lower()
        return any(indicator in user_lower for indicator in bot_indicators) or user_lower.endswith('[bot]')
    
    def get_prs(self, count: int = 100, state: str = "closed", exclude_bots: bool = True) -> List[Dict]:
        """Busca a lista de PRs do repositório com filtros"""
        prs = []
        page = 1
        per_page = min(100, count)
        
        while len(prs) < count:
            url = f"{self.base_url}/pulls"
            params = {
                "state": state,           # apenas closed
                "per_page": per_page,
                "page": page,
                "sort": "created",
                "direction": "desc"       # mais recentes primeiro
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code != 200:
                self.safe_print(f"Erro ao buscar PRs: {response.status_code} - {response.text}")
                break
            
            page_prs = response.json()
            if not page_prs:
                break
            
            # Aplicar filtro de bots se solicitado
            if exclude_bots:
                filtered_prs = [
                    pr for pr in page_prs 
                    if not self.is_bot_user(pr["user"]["login"])
                ]
                prs.extend(filtered_prs)
            else:
                prs.extend(page_prs)
            
            page += 1
            
            # Respeitar rate limit
            time.sleep(0.1)
        
        return prs[:count]
    
    def get_pr_comments(self, pr_number: int, exclude_bots: bool = True) -> List[Dict]:
        """Busca todos os comentários de um PR específico"""
        comments = []
        page = 1
        
        while True:
            # Buscar comentários da issue (inclui comentários gerais do PR)
            url_issue = f"{self.base_url}/issues/{pr_number}/comments"
            params = {
                "per_page": 100,
                "page": page
            }
            
            response = requests.get(url_issue, headers=self.headers, params=params)
            
            if response.status_code != 200:
                self.safe_print(f"Erro ao buscar comentários do PR #{pr_number}: {response.status_code}")
                break
            
            page_comments = response.json()
            if not page_comments:
                break
            
            # Filtrar comentários de bots
            if exclude_bots:
                filtered_comments = [
                    comment for comment in page_comments
                    if not self.is_bot_user(comment["user"]["login"])
                ]
                comments.extend(filtered_comments)
            else:
                comments.extend(page_comments)
            
            page += 1
            time.sleep(0.1)
        
        return comments
    
    def get_review_comments(self, pr_number: int, exclude_bots: bool = True) -> List[Dict]:
        """Busca comentários de review específicos (diferente dos comentários gerais)"""
        review_comments = []
        page = 1
        
        while True:
            url = f"{self.base_url}/pulls/{pr_number}/comments"
            params = {
                "per_page": 100,
                "page": page
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code != 200:
                self.safe_print(f"Erro ao buscar review comments do PR #{pr_number}: {response.status_code}")
                break
            
            page_comments = response.json()
            if not page_comments:
                break
            
            # Filtrar comentários de bots
            if exclude_bots:
                filtered_comments = [
                    comment for comment in page_comments
                    if not self.is_bot_user(comment["user"]["login"])
                ]
                review_comments.extend(filtered_comments)
            else:
                review_comments.extend(page_comments)
            
            page += 1
            time.sleep(0.1)
        
        return review_comments
    
    def get_all_prs_comments(self, pr_count: int = 100, state: str = "closed", exclude_bots: bool = True) -> Dict[str, Any]:
        """Busca comentários de todos os PRs com filtros"""
        self.safe_print(f"Buscando {pr_count} PRs (state: {state}, exclude_bots: {exclude_bots}) do repositório {self.owner}/{self.repo}...")
        
        prs = self.get_prs(pr_count, state, exclude_bots)
        all_data = {
            "repository": f"{self.owner}/{self.repo}",
            "filters": {
                "state": state,
                "exclude_bots": exclude_bots
            },
            "total_prs": len(prs),
            "prs": []
        }
        
        for i, pr in enumerate(prs, 1):
            pr_number = pr["number"]
            pr_title = pr["title"]
            pr_author = pr["user"]["login"]
            
            # Usar safe_print para evitar problemas de Unicode
            self.safe_print(f"Processando PR #{pr_number}: '{pr_title}' por {pr_author} ({i}/{len(prs)})")
            
            # Buscar ambos tipos de comentários
            issue_comments = self.get_pr_comments(pr_number, exclude_bots)
            review_comments = self.get_review_comments(pr_number, exclude_bots)
            
            all_comments = issue_comments + review_comments
            
            pr_data = {
                "number": pr_number,
                "title": pr_title,
                "state": pr["state"],
                "user": pr_author,
                "created_at": pr["created_at"],
                "updated_at": pr["updated_at"],
                "closed_at": pr.get("closed_at"),
                "merged_at": pr.get("merged_at"),
                "comments_count": len(all_comments),
                "issue_comments_count": len(issue_comments),
                "review_comments_count": len(review_comments),
                "comments": [
                    {
                        "id": comment["id"],
                        "user": comment["user"]["login"],
                        "body": comment["body"],
                        "created_at": comment["created_at"],
                        "updated_at": comment["updated_at"],
                        "comment_type": "review" if "pull_request_review_id" in comment else "issue"
                    }
                    for comment in all_comments
                ]
            }
            
            all_data["prs"].append(pr_data)
            
            # Respeitar rate limit entre PRs
            time.sleep(0.2)
        
        return all_data
    
    def save_to_file(self, data: Dict, filename: str = None):
        current_dir = os.path.dirname(os.path.abspath(__file__))

        """Salva os dados em um arquivo JSON"""
        if filename is None:
            filters = data["filters"]
            state = filters["state"]
            exclude_bots = filters["exclude_bots"]
            filename = f"pr_comments_{self.owner}_{self.repo}_{state}_nobots_{exclude_bots}.json"
        
        output_path = os.path.join(current_dir, filename)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        self.safe_print(f"Dados salvos em {filename}")

# Configuração e uso
def main():
    # CONFIGURAÇÕES
    GITHUB_TOKEN = "seu_token"  # Token de acesso pessoal do GitHub
    REPO_OWNER = "owner_repositorio"  # Ex: "facebook"
    REPO_NAME = "nome_repositorio"  # Ex: "react"
    
    # Criar instância
    github = GitHubPRComments(
        token=GITHUB_TOKEN,
        owner=REPO_OWNER,
        repo=REPO_NAME
    )
    
    # Buscar comentários APENAS de PRs closed e sem bots
    data = github.get_all_prs_comments(
        pr_count=100,
        state="closed",           # apenas PRs fechados
        exclude_bots=True         # excluir bots
    )
    
    # Salvar resultados
    github.save_to_file(data)
    
    # Estatísticas
    total_comments = sum(pr["comments_count"] for pr in data["prs"])
    if data["prs"]:
        pr_with_most_comments = max(data["prs"], key=lambda x: x["comments_count"])
        
        github.safe_print(f"\n--- ESTATÍSTICAS ---")
        github.safe_print(f"PRs processados: {data['total_prs']}")
        github.safe_print(f"Total de comentários: {total_comments}")
        github.safe_print(f"PR com mais comentários: #{pr_with_most_comments['number']} ({pr_with_most_comments['comments_count']} comentários)")
        github.safe_print(f"Filtros aplicados: {data['filters']}")
    else:
        github.safe_print("Nenhum PR encontrado com os filtros especificados.")

if __name__ == "__main__":
    main()