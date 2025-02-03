import os
from gvm.connections import UnixSocketConnection
from gvm.protocols.gmp import GMP
from gvm.transforms import EtreeCheckCommandTransform
from dotenv import load_dotenv
import xml.etree.ElementTree as ET
# Carregar variáveis de ambiente
load_dotenv()
# Obter os valores das variáveis de ambiente
path = os.getenv('GVMD_SOCKET_PATH')
username = os.getenv('GVMD_USERNAME')
password = os.getenv('GVMD_PASSWORD')
# Estabelecer conexão com o Unix Socket
connection = UnixSocketConnection(path=path)
transform = EtreeCheckCommandTransform()


with GMP(connection=connection, transform=transform) as gmp:
    
    try:
        # Autentica no servidor
        gmp.authenticate(username=username, password=password)
        
        # Busca todas as tarefas
        """tasks = gmp.get_tasks()
        
        task_id = None
        task_name_part = "scan"  # Substitua por uma palavra ou parte do nome da tarefa
        
        #Verifica todas as tarefas e busca a que contém o nome desejado
        for task in tasks.findall('task'):
            task_name = task.findtext('name')
            if task_name_part.lower() in task_name.lower():  # Verifica se a palavra está no nome da tarefa
                task_id = task.get('id')
                print(f"Tarefa encontrada: {task_name} (ID: {task_id})")
                break
        
        if not task_id:
            raise Exception(f"Nenhuma tarefa encontrada com a palavra '{task_name_part}' no nome.")"""
        
        # Obtém o relatório da tarefa usando o task_id
        reports = gmp.get_report(
            report_id='661d8ef8-d041-4dd0-b4f1-8ccccd7a63d0',  # Usa o task_id como report_id
            #filter_string="scan",
            report_format_id="c1645568-627a-11e3-a660-406186ea4fc5",  # Formato do relatório (XML)
            details=True
        )
        report_str = ET.tostring(reports, encoding="unicode", method="xml")
        # Salva o relatório ou faz o que for necessário com ele
        print("Relatório obtido com sucesso:", report_str)

    except Exception as e:
        print(f"Erro: {e}")
        
        