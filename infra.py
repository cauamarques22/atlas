import stat
import datetime
import json
import git
import shutil
import os
import time
import subprocess
from pathlib import Path

with open("config.json") as f:
    CONFIG = json.load(f)

HOME = Path(__file__).parent
HOME = str(HOME)
BASE_REPO_PATH = HOME + r"\repo"

def handle_remove_readonly(func, path, exc):
    if func in (os.rmdir, os.remove, os.unlink):
        # Muda o arquivo para modo escrita
        os.chmod(path, stat.S_IWRITE)
        # Tenta apagar de novo
        func(path)

#Limpa a pasta repo
def limpar_pasta(pasta):
    for nome in os.listdir(pasta):
        caminho = os.path.join(pasta, nome)
        if os.path.isfile(caminho) or os.path.islink(caminho):
            try:
                os.remove(caminho)
            except:
                handle_remove_readonly(os.remove, caminho, "")
        elif os.path.isdir(caminho):
            shutil.rmtree(caminho, onerror=handle_remove_readonly)

def write_configs(configs):
    with open("config.json", "w+") as file:
        json.dump(configs, file, indent=4, ensure_ascii=False)

#Deleta pasta repo
def delete_repo():
    shutil.rmtree(BASE_REPO_PATH, onerror=handle_remove_readonly)

def pasta_vazia(caminho):
    """
    Verifica se uma pasta está vazia.
    
    :param caminho: Caminho da pasta a ser verificada.
    :return: True se a pasta estiver vazia, False caso contrário.
    """
    if not os.path.isdir(caminho):
        raise ValueError(f"'{caminho}' não é uma pasta válida.")
    
    return len(os.listdir(caminho)) == 0

def list_infrastructure():
    """
    Lista todos os blocos de infraestrutura
    """
    print("Blocos de Infraestrutura")
    for infrastructure_b in CONFIG["infrastructure_blocks"].keys():
        print(f" - {infrastructure_b}")

class GitHandler():

    def get_repo(self):
        self.repo = git.Repo(BASE_REPO_PATH)
        self.origin = self.repo.remotes.origin
        
        self.origin.fetch()
        remote_head = self.origin.refs.HEAD
        self.default_branch = remote_head.reference.name.split("/")[-1]

    def create_repo(self, infrastructure_b_name: str, skip_input: bool=False, repo_url=""):
        # Cria o diretório do repositório
        os.makedirs(BASE_REPO_PATH, exist_ok=True)
        
        #Inicializa o repositório
        self.repo = git.Repo.init(BASE_REPO_PATH)

        if not skip_input:
            #Pega a ssh do repositório remoto
            repo_url = input("Informe o ssh do repositório: ")

        #Verifica se já tem origin nos remotes
        if "origin" not in [remote.name for remote in self.repo.remotes]:
            self.repo.create_remote("origin", repo_url)
        #Faz o fetch do remote
        self.origin = self.repo.remotes.origin
        self.origin.fetch()

        #Pega o head e o default branch
        remote_head = self.origin.refs.HEAD
        self.default_branch = remote_head.reference.name.split("/")[-1]
        
        #Faz o checkout para a branch default
        self.repo.git.checkout("-B", self.default_branch)
        self.origin.pull(self.default_branch)
        
        #Atualiza o ssh do repositório remoto daquele Bloco de Infraestrutura
        CONFIG["infrastructure_blocks"][infrastructure_b_name]["repo_ssh"] = repo_url

        if CONFIG["open_code_after_pull"]:
            subprocess.run(f"cd {BASE_REPO_PATH} && code .", shell=True)

    def add_and_commit(self):
        if self.repo.is_dirty(untracked_files=True):
            #Adiciona todas as alterações e commita
            self.repo.git.add(A=True)
            self.repo.index.commit(f"Atualização automática via script ({datetime.datetime.now().date()}) ")
            time.sleep(1)
            self.origin.push(self.default_branch)
            limpar_pasta(BASE_REPO_PATH)
        else:
            limpar_pasta(BASE_REPO_PATH)

class Deploy():
    def __init__(self):
        ...
    def deploy(self):
        resultado = subprocess.run(f"terraform init", shell=True, cwd=BASE_REPO_PATH, capture_output=True, text=True)
        print(resultado.stdout)
        resultado = subprocess.run(f"terraform apply -auto-approve", shell=True, cwd=BASE_REPO_PATH, capture_output=True, text=True)
        if resultado.returncode != 0:
            print("Erro:")
            print(resultado.stdout)
            print(resultado.stderr)

    def destroy(self):
        resultado = subprocess.run(f"terraform init", shell=True, cwd=BASE_REPO_PATH, capture_output=True, text=True)
        if resultado.returncode != 0:
            print("Erro:")
            print(resultado.stdout)
            print(resultado.stderr)
        print(resultado.stdout)

        resultado = subprocess.run(f"terraform destroy -auto-approve", shell=True, cwd=BASE_REPO_PATH, capture_output=True, text=True)
        if resultado.returncode != 0:
            print("Erro:")
            print(resultado.stdout)
            print(resultado.stderr)
        print(resultado.stdout)


githandler = GitHandler()
deploy_handler = Deploy()

command = input("Digite um comando: ")

#Lista todos os blocos de infraestrutura
if command == "atlas list-struct":
    list_infrastructure()

#Cria um bloco de infraestrutura
elif command == "atlas create-struct":
    infrastructure_b_name = input("Informe o Nome do Bloco de Infraestrutura: ")
    repo_url = input("Digite a url do repositório: ")
    #Inicializa um dicionário no nome do bloco de infraestrutura
    CONFIG["infrastructure_blocks"][infrastructure_b_name] = {"repo_ssh":repo_url}

#Salva o bloco e faz o commit.
elif command == "atlas save":
    githandler.get_repo()
    githandler.add_and_commit()

#Faz o pull do bloco e abre o editor
elif command == "atlas manage":
    if not pasta_vazia(BASE_REPO_PATH):
        raise Exception("A Pasta de Repositórios está com um bloco dentro. Salve e elimine os arquivos.")
    list_infrastructure()
    infrastructure_b_name = input("Digite o nome do Bloco de Infraestrutura: ")
    githandler.create_repo(infrastructure_b_name, skip_input=True, repo_url=CONFIG["infrastructure_blocks"][infrastructure_b_name]["repo_ssh"])

#Faz o deploy do bloco de infraestrutura a partir dos arquivos terraform dele
elif command == "atlas deploy":
    deploy_handler.deploy()

#Faz o destroy do bloco de infraestrutura a partir dos arquivos terraform dele
elif command == "atlas destroy":
    deploy_handler.destroy()

#Deleta todos os arquivos da pasta repo
elif command == "delete":
    limpar_pasta(BASE_REPO_PATH)

write_configs(CONFIG)