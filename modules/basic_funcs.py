import click
import modules.struct_utils as struct_utils

CONTEXT = None
CONSOLE = None

def list_infrastructure():
    """
    Lista todos os blocos de infraestrutura
    """
    for infrastructure_b in CONTEXT.CONFIG["infrastructure_blocks"].keys():
        print(f" - {infrastructure_b}")

#Create, Read, Delete
@click.argument("arg")
@click.command()
def show(arg):
    if arg == "struct":
        CONSOLE.print("[bold green]- Listando Blocos de Infraestrutura.")
        list_infrastructure()
    else:
        CONSOLE.print(f"[bold red] Comando {arg} desconhecido.")
    
@click.command()
@click.argument("tipo")
@click.argument("nome")
@click.argument("url")
def create(tipo, nome, url):
    if tipo == "struct":
        #Inicializa um dicionário no nome do bloco de infraestrutura
        CONSOLE.print(f"[bold green]- Criando Bloco de Infraestrutura {nome}")
        CONTEXT.CONFIG["infrastructure_blocks"][nome] = {"repo_ssh":url}
        struct_utils.write_configs(CONTEXT.CONFIG)
    else:
        CONSOLE.print(f"[bold red] Comando {tipo} desconhecido.")
   
@click.command()
@click.argument("tipo")
@click.option("--name")
@click.option("--y", is_flag=True)
def delete(tipo, name, y):
    #Pendente desenvolvimento
    if tipo == "struct" and name:
        if y:
            CONSOLE.print(f"-⚠️ Deletando Bloco de Infraestrutura: {name}")
        else:
            res = CONSOLE.input(f"[bold blue]-⚠️ Tem certeza que deseja deletar o Bloco de Infraestrutura:[/] {name}? \n[ y / n ]:")
            if res == "y":
                CONSOLE.print(f"[bold red]-⚠️ Deletando Bloco de Infraestrutura:[/] {name}")
            else:
                CONSOLE.print(f"- Operação abortada.")
    elif tipo == "repo":
        struct_utils.limpar_pasta(CONTEXT.repo_path)
