import json
import shutil
import stat
import os
from pathlib import Path

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