import os
from gvm.connections import UnixSocketConnection
from gvm.protocols.gmp import GMP
from gvm.transforms import EtreeCheckCommandTransform
from dotenv import load_dotenv
# Carregar variáveis de ambiente
load_dotenv()
# Obter os valores das variáveis de ambiente
path = os.getenv('GVMD_SOCKET_PATH')
username = os.getenv('GVMD_USERNAME')
password = os.getenv('GVMD_PASSWORD')
host = os.getenv('GVMD_HOST')
port_list_name = os.getenv('GVMD_PORT_LIST_NAME', 'All IANA assigned TCP and UDP')  # Nome da lista de portas desejada
# Estabelecer conexão com o Unix Socket
connection = UnixSocketConnection(path=path)
transform = EtreeCheckCommandTransform()

print(password is not None)

task_name = input("Digite um nome de task para o scan: ")
# Criar uma instância do GMP e iniciar uma sessão
with GMP(connection=connection, transform=transform) as gmp:
    try:
        # Autenticar com as credenciais fornecidas
        gmp.authenticate(username, password)
        # Obter a lista de portas pelo nome
        port_lists = gmp.get_port_lists()
        port_list_id = None
        for port_list in port_lists.findall('port_list'):
            if port_list.findtext('name') == port_list_name:
                port_list_id = port_list.get('id')
                break
        if not port_list_id:
            raise Exception(f"Port list '{port_list_name}' not found.")
        # Verificar se o alvo já existe
        targets = gmp.get_targets()
        target_id = None
        for target in targets.findall('target'):
            if target.findtext('name') == "My Target" or target.findtext('hosts') == host:
                target_id = target.get('id')
                break
        # Criar um novo alvo se não existir
        if not target_id:
            target = gmp.create_target(
                name="My Target",
                hosts=[host],
                comment="My Target",
                port_list_id=port_list_id,
            )
            target_id = target.get("id")
        # Obter ID de configuração (Scan Configuration)
        configs = gmp.get_scan_configs()
        config_id = None
        for config in configs.findall('config'):
            if config.findtext('name') == 'Full and fast':  # Use o nome apropriado
                config_id = config.get('id')
                break
        if not config_id:
            raise Exception("Scan configuration 'Full and fast' not found.")
        # Obter ID do scanner
        scanners = gmp.get_scanners()
        scanner_id = None
        for scanner in scanners.findall('scanner'):
            if scanner.findtext('name') == 'OpenVAS Default':  # Use o nome apropriado
                scanner_id = scanner.get('id')
                break
        if not scanner_id:
            raise Exception("Scanner 'OpenVAS Default' not found.")
        # Criar uma tarefa usando o ID do alvo, configuração e scanner
        task = gmp.create_task(
            name=task_name,
            config_id=config_id,
            target_id=target_id,
            scanner_id=scanner_id,
        )
        print(task)
    except Exception as e:
        print(f"Erro: {e}")