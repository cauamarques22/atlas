import subprocess
import click

class Deploy():
    def __init__(self, context=None):
        self.context_instance = context
    
    def deploy(self):
        resultado = subprocess.run(f"terraform init", shell=True, cwd=self.context_instance.repo_path, capture_output=True, text=True)
        print(resultado.stdout)
        resultado = subprocess.run(f"terraform apply -auto-approve", shell=True, cwd=self.context_instance.repo_path, capture_output=True, text=True)
        if resultado.returncode != 0:
            print("Erro:")
            print(resultado.stdout)
            print(resultado.stderr)

    def destroy(self):
        resultado = subprocess.run(f"terraform init", shell=True, cwd=self.context_instance.repo_path, capture_output=True, text=True)
        if resultado.returncode != 0:
            print("Erro:")
            print(resultado.stdout)
            print(resultado.stderr)
        print(resultado.stdout)

        resultado = subprocess.run(f"terraform destroy -auto-approve", shell=True, cwd=self.context_instance.repo_path, capture_output=True, text=True)
        if resultado.returncode != 0:
            print("Erro:")
            print(resultado.stdout)
            print(resultado.stderr)
        print(resultado.stdout)

deploy_handler = Deploy()
CONTEXT = None

#Deploy
@click.command()
def deploy():
    deploy_handler.deploy()

@click.command()
def destroy():
    deploy_handler.destroy()
