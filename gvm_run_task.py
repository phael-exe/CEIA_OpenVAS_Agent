import os
import re
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

        #Criação do alvo
        targets = gmp.get_targets()

        target_id = None
        for target in targets.findall('target'):
            target_name = target.findtext('name')
            target_id = target.get('id')
            print(f"Alvo encontrado -> Nome: {target_name}, ID: {target_id}")

            if target_name == "ALVO TESTE":
                target_id = target_id
                print(f"Alvo correto identificado: {target_id}")
                break

            if not target_id:
                raise Exception("Alvo 'ALVO TESTE' não encontrado!")


        scanners = gmp.get_scanners()

        scanner_id = None
        for scanner in scanners.findall('scanner'):
            scanner_name = scanner.findtext('name')
            scanner_id = scanner.get('id')
            print(f"Scanner encontrado -> Nome: {scanner_name}, ID: {scanner_id}")  

            if scanner_name == "OpenVAS Default":  
                scanner_id = scanner_id
                print(f"Scanner correto identificado: {scanner_id}")
                break

        if not scanner_id:
            raise Exception("Scanner 'OpenVAS Default' não encontrado!")

        task_test = gmp.create_task(name=task_name, config_id=scan_config_id, target_id=target_id, scanner_id=scanner_id)

        print(f"Tarefa criada com sucesso: {task_test}")

        #Agora verificar a task e rodá-la
        tasks = gmp.get_tasks()

        for task in tasks.findall('task'):
            task_name = task.findtext('name')
            task_id = task.get('id')
            print(f"Tarefa encontrada -> Nome: {task_name}, ID: {task_id}")

            if task_name == task_name:
                task_id = task_id
                print(f"Tarefa correta encontrada: {task_id}")
                break
        
        if not task_id:
            raise Exception(f"Tarefa {task_name} não encontrada!")
        
        start = gmp.start_task(task_id=task_id)

        print(start)
    

    except Exception as e:
        print(f"Erro: {e}")
        





