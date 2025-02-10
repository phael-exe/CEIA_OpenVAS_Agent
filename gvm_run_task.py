import os
from gvm.connections import UnixSocketConnection
from gvm.protocols.gmp import GMP
from gvm.transforms import EtreeCheckCommandTransform
from dotenv import load_dotenv

load_dotenv()

path = os.getenv('GVMD_SOCKET_PATH')
username = os.getenv('GVMD_USERNAME')
password = os.getenv('GVMD_PASSWORD')
host = os.getenv('GVMD_HOST')
port_list_id = os.getenv('GVMD_PORT_LIST_ID')
target_id = os.getenv('GVMD_TARGET_ID')
scan_config_id = os.getenv('GVMD_SCAN_CONFIG_ID')
scanner_id = os.getenv('GVMD_SCANNER_ID')


connection = UnixSocketConnection(path=path)
transform = EtreeCheckCommandTransform()

#print(scanner_id is not None)

task_name = input("Digite um nome de task para o scan: ")

with GMP(connection=connection, transform=transform) as gmp:
    try:
        gmp.authenticate(username=username, password=password)

        targets = gmp.get_
        target_id = None


        scan_config_id = gmp.get_scan_config(config_id=scan_config_id)

        scanners = gmp.get_scanners()

        # 🔹 Procurar pelo scanner correto
        scanner_id = None
        for scanner in scanners.findall('scanner'):
            name = scanner.findtext('name')
            current_id = scanner.get('id')
            print(f"Scanner encontrado -> Nome: {name}, ID: {current_id}")  # Debug

            if name == "OpenVAS Default":  # Nome do scanner que você quer usar
                scanner_id = current_id
                print(f"🟢 Scanner correto identificado: {scanner_id}")
                break

        if not scanner_id:
            raise Exception("Scanner 'OpenVAS Default' não encontrado!")

        task = gmp.create_task(name=task_name, config_id=scan_config_id, target_id=target_id, scanner_id=scanner_id)

        checkpoint = gmp.get_tasks(filter_string=str(task_name))

        #start = gmp.start_task(task_id=str)

        print(f"Tarefa criada com sucesso: {task}")

        print(f"Tarefa encontrada com sucesso: {checkpoint}")

        

    except Exception as e:
        print(f"Erro: {e}")
        





