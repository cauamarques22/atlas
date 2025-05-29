import json
import os
import click
import rich_click
import sys
rich_click.rich_click.MAX_WIDTH = 100
rich_click.rich_click.USE_RICH_MARKUP = True

from rich.tree import Tree
from rich.console import Console
from rich.table import Table
from pathlib import Path

#Módulos da aplicação
import modules.struct_utils as struct_utils
import modules.git_manager as git_manager
import modules.deploy_manager as deploy_manager
import modules.basic_funcs as basic_funcs

JSON_EXPECTED_KEYS = ["open_code_after_pull", "atlas_home_path", "atlas_repo_path", "infrastructure_blocks"]

def context_middleware():
    if not context.repo_path or not context.home:
        console.print("[bold red]- O caminho do repositório não foi encontrado.")
        exit()

def config_file_middleware():
    try:
        with open("config.json", "r") as file:
            json.load(file)
    except FileNotFoundError:
        console.print("[bold red]- Arquivo de configurações config.json não encontrado.\n- Execute: [bold blue]atlas init")
        exit()

class Context:
    def __init__(self):
        self.home: str| None = None
        self.repo_path: str | None = None
        self.CONFIG = {
            "open_code_after_pull": True,
            "atlas_home_path": "",
            "atlas_repo_path": "",
            "infrastructure_blocks":{}
        }
        self.read_json()
        self.update_context()
    
    def read_json(self):
        try:
            with open("config.json", "r") as f:
                self.CONFIG = json.load(f)
        except json.JSONDecodeError:
            pass
        except FileNotFoundError:
            pass

    def update_context(self):
        self.home = self.CONFIG["atlas_home_path"]
        self.repo_path = self.CONFIG["atlas_repo_path"]
    
    def verify_json(self):
        for key in self.CONFIG.keys():
            if key not in JSON_EXPECTED_KEYS:
                console.print("[bold red]- O arquivo config.json está com valores corrompidos. Por favor, execute o comando init novamente.")
                exit()

class ContextMiddleware(click.Group):
    def invoke(self, ctx):
        config_file_middleware()
        context_middleware()
        return super().invoke(ctx)

context = Context()
console = Console()
git_manager.githandler.context_instance = context
git_manager.CONTEXT = context

deploy_manager.deploy_handler.context_instance = context
deploy_manager.CONTEXT = context

basic_funcs.CONTEXT = context
basic_funcs.CONSOLE = console

@click.group(cls=ContextMiddleware)
def cli():
    pass

#Adicionando os comandos do cli
cli.add_command(git_manager.save)
cli.add_command(git_manager.manage)
cli.add_command(basic_funcs.show)
cli.add_command(basic_funcs.create)
cli.add_command(basic_funcs.delete)

#Inicialização
def standalone_init():
    path = os.getcwd()
    path = Path(path)
    context.CONFIG["atlas_home_path"] = path
    context.CONFIG["atlas_repo_path"] = path.joinpath("repo")
    struct_utils.write_configs(context.CONFIG)

if len(sys.argv) > 1 and sys.argv[1] == "init":
    standalone_init()
else:    
    cli()

struct_utils.write_configs(context.CONFIG)