import click
import subprocess
import git
import os
import modules.struct_utils as struct_utils
import time
import datetime

class GitHandler():

    def __init__(self, context=None):
        self.context_instance = context

    #Necessário adicionar uma lógica de validação para verificar se o repositório de fato existe.
    def get_repo(self):
        self.repo = git.Repo(self.context_instance.repo_path)
        self.origin = self.repo.remotes.origin
        
        self.origin.fetch()
        remote_head = self.origin.refs.HEAD
        self.default_branch = remote_head.reference.name.split("/")[-1]

    def create_repo(self, infrastructure_b_name: str, repo_url=""):
        # Cria o diretório do repositório
        os.makedirs(self.context_instance.repo_path, exist_ok=True)
        
        #Inicializa o repositório
        self.repo = git.Repo.init(self.context_instance.repo_path)

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
        self.context_instance.CONFIG["infrastructure_blocks"][infrastructure_b_name]["repo_ssh"] = repo_url

        if self.context_instance.CONFIG["open_code_after_pull"]:
            subprocess.run(f"cd {self.context_instance.repo_path} && code .", shell=True)

    def add_and_commit(self):
        if self.repo.is_dirty(untracked_files=True):
            #Adiciona todas as alterações e commita
            self.repo.git.add(A=True)
            self.repo.index.commit(f"Atualização automática via script ({datetime.datetime.now().date()}) ")
            time.sleep(1)
            self.origin.push(self.default_branch)
            struct_utils.limpar_pasta(self.context_instance.repo_path)
        else:
            struct_utils.limpar_pasta(self.context_instance.repo_path)

githandler = GitHandler()
CONTEXT = None

#Comandos Git
@click.command()
def save():
    githandler.get_repo()
    githandler.add_and_commit()

@click.command()
@click.argument("name")
def manage(name):
    try:
        if not struct_utils.pasta_vazia(CONTEXT.repo_path):
            raise Exception("A Pasta de Repositórios está com um bloco dentro. Salve e elimine os arquivos.")
    except ValueError:
        pass
    githandler.create_repo(name, repo_url=CONTEXT.CONFIG["infrastructure_blocks"][name]["repo_ssh"])

