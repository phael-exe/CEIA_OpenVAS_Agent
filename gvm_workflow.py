import os
from gvm.connections import UnixSocketConnection
from gvm.protocols.gmp import GMP
from gvm.transforms import EtreeCheckCommandTransform
from dotenv import load_dotenv

class ConnectionManager:
    def __init__(self, path):
        self.path = path

    def connect(self):
        """Estabelece a conexão com o Unix Socket e retorna o objeto GMP."""
        connection = UnixSocketConnection(path=self.path)
        transform = EtreeCheckCommandTransform()
        return GMP(connection=connection, transform=transform)

class AuthenticationManager:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def authenticate(self, gmp):
        """Autentica o usuário usando o GMP."""
        gmp.authenticate(self.username, self.password)


class TargetManager:

    def get_target_id(self, gmp):
        """Verifica se o alvo já existe e retorna seu ID """
        targets = gmp.get_targets()
        
        target_id = None
        for target in targets.findall('target'):
            target_name = target.findtext('name')
            target_id = target.get('id')
            #print(f"Alvo encontrado -> Nome: {target_name}, ID: {target_id}")

            if target_name == "ALVO TESTE":
                target_id = target_id
                #print(f"Alvo correto identificado: {target_id}")
                break

            if not target_id:
                raise Exception("Alvo 'ALVO TESTE' não encontrado!")
            
        return target_id

class ConfigManager:
    def get_config_id(self, gmp):
        """Obtém o ID da configuração de scan pelo nome."""
        configs = gmp.get_scan_configs()
        for config in configs.findall('config'):
            if config.findtext('name') == 'Full and fast':
                return config.get('id')
        raise Exception("Scan configuration 'Full and fast' not found.")

class ScannerManager:
    def get_scanner_id(self, gmp):
        """Obtém o ID do scanner pelo nome."""
        scanners = gmp.get_scanners()
        for scanner in scanners.findall('scanner'):
            if scanner.findtext('name') == 'OpenVAS Default':
                return scanner.get('id')
        raise Exception("Scanner 'OpenVAS Default' not found.")

class TaskCreator:
    def __init__(self):
        pass

    def create_task(self, gmp, name, config_id, target_id, scanner_id):
        """Cria uma tarefa de scan."""
        return gmp.create_task(
            name=name,
            config_id=config_id,
            target_id=target_id,
            scanner_id=scanner_id,
        )

class TaskManager:
    def __init__(self, target_manager, config_manager, scanner_manager, task_creator):
        self.target_manager = target_manager
        self.config_manager = config_manager
        self.scanner_manager = scanner_manager
        self.task_creator = task_creator

    def prepare_task(self, gmp, task_name):
        """Prepara os IDs necessários para criar uma tarefa e chama o TaskCreator."""
        target_id = self.target_manager.get_target_id(gmp)
        config_id = self.config_manager.get_config_id(gmp)
        scanner_id = self.scanner_manager.get_scanner_id(gmp)
        return self.task_creator.create_task(gmp, task_name, config_id, target_id, scanner_id)
    
class TaskStarter:
    def start_task(self, gmp, task_name):
        """Inicia uma tarefa existente pelo nome."""
        tasks = gmp.get_tasks()
        
        for task in tasks.findall('task'):
            if task.findtext('name') == task_name:
                task_id = task.get('id')
                return gmp.start_task(task_id=task_id)
        
        raise Exception(f"Tarefa '{task_name}' não encontrada!")

class GVMWorkflow:
    def __init__(self):
        load_dotenv()
        self.connection_manager = ConnectionManager(os.getenv('GVMD_SOCKET_PATH'))
        self.auth_manager = AuthenticationManager(
            os.getenv('GVMD_USERNAME'), os.getenv('GVMD_PASSWORD')
        )
        self.target_manager = TargetManager()
        self.config_manager = ConfigManager()
        self.scanner_manager = ScannerManager()
        self.task_creator = TaskCreator()
        self.task_manager = TaskManager(
            self.target_manager, self.config_manager, self.scanner_manager, self.task_creator
        )
        self.task_starter = TaskStarter()

    def run(self):
        """Executa o fluxo completo."""
        with self.connection_manager.connect() as gmp:
            try:
                self.auth_manager.authenticate(gmp)
                task_name = input("Enter a task name for the scan.: ")
                task = self.task_manager.prepare_task(gmp, task_name)
                print("Task criada com sucesso:", task)

                start_response = self.task_starter.start_task(gmp, task_name)
                print("Task started successfully.:", start_response)
                print("Running task. ...")
            except Exception as e:
                print(f"Error: {e}")

# Uso da classe
if __name__ == "__main__":
    workflow = GVMWorkflow()
    workflow.run()
