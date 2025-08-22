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
    def create_target(self, gmp, target_name, target_host, port_list_id):
        """Cria um novo alvo e retorna seu ID."""
        target = gmp.create_target(
            name=target_name,
            hosts=[target_host],
            alive_test='Scan Config Default',
            allow_simultaneous_ips=True,
            port_list_id=port_list_id
        )
        print(f"Target created successfully: {target}")
        return target.get('id')

    def get_port_lists(self, gmp):
        """Obtém as listas de portas disponíveis e retorna um dicionário com nome e ID."""
        port_lists = gmp.get_port_lists()
        port_list_dict = {}
        
        for port_list in port_lists.findall('port_list'):
            name = port_list.findtext('name')
            id = port_list.get('id')
            port_list_dict[name] = id
        
        return port_list_dict

    def get_port_list_id_by_name(self, gmp, name):
        """Obtém o ID de uma lista de portas pelo nome."""
        port_lists = self.get_port_lists(gmp)
        for port_list_name, port_list_id in port_lists.items():
            if port_list_name == name:
                return port_list_id
        raise Exception(f"Port list '{name}' not found!")

    def get_or_create_target_id(self, gmp, target_host, target_name=None, port_list_name="All IANA assigned TCP"):
        """Obtém o ID de um alvo existente ou cria um novo se não existir."""
        targets = gmp.get_targets()
        for target in targets.findall('target'):
            if target.findtext('hosts') == target_host:
                print(f"Using existing target: {target.findtext('name')} ({target_host})")
                return target.get('id')

        # Se o alvo não existe, cria um novo
        if not target_name:
            target_name = f"Target - {target_host}"

        port_list_id = self.get_port_list_id_by_name(gmp, port_list_name)

        target = gmp.create_target(
            name=target_name,
            hosts=[target_host],
            alive_test='Scan Config Default',
            allow_simultaneous_ips=True,
            port_list_id=port_list_id
        )
        print(f"New target created: {target_name} ({target_host})")
        return target.get('id')

    def get_target_id(self, gmp):
        """Permite ao usuário escolher um alvo existente ou criar um novo."""
        choice = input("\nDo you want to create a new target? (yes/no): ").strip().lower()
        
        if choice == 'yes':
            return self.create_target(gmp)
        
        print("\nExisting Targets:")
        targets = gmp.get_targets()
        target_dict = {}
        
        for target in targets.findall('target'):
            target_name = target.findtext('name')
            target_id = target.get('id')
            target_dict[target_name] = target_id
            print(f"- {target_name}")
        
        selected_target = input("\nType the exact name of the target you want to use: ").strip()
        if selected_target in target_dict:
            return target_dict[selected_target]
        
        raise Exception("\nTarget not found!")

class ConfigManager:
    def get_config_id(self, gmp):
        """Obtém o ID da configuração de scan pelo nome."""
        configs = gmp.get_scan_configs()
        for config in configs.findall('config'):
            if config.findtext('name') == 'Full and fast':
                return config.get('id')
        raise Exception("\nScan configuration 'Full and fast' not found.")

class ScannerManager:
    def get_scanner_id(self, gmp):
        """Obtém o ID do scanner pelo nome."""
        scanners = gmp.get_scanners()
        for scanner in scanners.findall('scanner'):
            if scanner.findtext('name') == 'OpenVAS Default':
                return scanner.get('id')
        raise Exception("\nScanner 'OpenVAS Default' not found.")

class TaskCreator:
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

    def prepare_task(self, gmp, task_name, target_host):
        """Prepara os IDs necessários para criar uma tarefa e chama o TaskCreator."""
        target_id = self.target_manager.get_or_create_target_id(gmp, target_host)
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
        
        raise Exception(f"\nTask '{task_name}' not found!")

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

    def run(self, task_name, target_host):
        """Executa o fluxo completo."""
        with self.connection_manager.connect() as gmp:
            try:
                self.auth_manager.authenticate(gmp)

                # Prepara e cria a tarefa
                task = self.task_manager.prepare_task(gmp, task_name, target_host)
                print("\nTask successfully created:", task)

                # Inicia a tarefa
                start_response = self.task_starter.start_task(gmp, task_name)
                print("\nTask started successfully:", start_response)
                print("\nRunning task...")
                return f"Task '{task_name}' for host '{target_host}' created and started successfully."
            except Exception as e:
                print(f"\nError: {e}")
                return f"Error creating or starting task: {e}"

if __name__ == "__main__":
    workflow = GVMWorkflow()
    # Example usage for testing
    # workflow.run("Test Task", "127.0.0.1")