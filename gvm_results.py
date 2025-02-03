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

class ResultManager:
    def __init__(self):
        pass
        
    def result():
        with GMP(connection=connection, transform=transform) as gmp:
            try:
                # Autentica no servidor
                gmp.authenticate(username=username, password=password)
        
                tasks = gmp.get_tasks()
        
                task_id = None
                task_name_part = "scan" # Substitua por uma palavra ou parte do nome da tarefa
        
                # Verifica todas as tarefas e busca a que contém o nome desejado
                for task in tasks.findall('task'):
                    task_name = task.findtext('name')
                    if task_name_part.lower() in task_name.lower():  # Verifica se a palavra está no nome da tarefa
                        task_id = task.get('id')
                        #print(f"Tarefa encontrada: {task_name} (ID: {task_id})")
                        break
        
                if not task_id:
                    raise Exception(f"Nenhuma tarefa encontrada com a palavra '{task_name_part}' no nome.")
        
                results = gmp.get_results(task_id=task_id)
        
                result_str = ET.tostring(results, encoding="unicode", method="xml")
                #print(f"Resultados obtidos com sucesso: {result_str}")
        
            except Exception as e:
                print(f"Erro: {e}")
                
        return result_str
                
                


