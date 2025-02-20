import os
from gvm.connections import UnixSocketConnection
from gvm.protocols.gmp import GMP
from gvm.transforms import EtreeCheckCommandTransform
from dotenv import load_dotenv
import xml.etree.ElementTree as ET
import pandas as pd
# Carregar variáveis de ambiente
load_dotenv()
# Obter os valores das variáveis de ambiente
path = os.getenv('GVMD_SOCKET_PATH')
username = os.getenv('GVMD_USERNAME')
password = os.getenv('GVMD_PASSWORD')
# Estabelecer conexão com o Unix Socket
connection = UnixSocketConnection(path=path)
transform = EtreeCheckCommandTransform()

class Report_Manager:
    def __init__(self):
        pass
    
    def report(self):
        with GMP(connection=connection, transform=transform) as gmp:
            try:
                # Autentica no servidor
                gmp.authenticate(username=username, password=password)
        
                # Busca todas as tarefas
                tasks = gmp.get_tasks()

                task_id = None
                task_name_part = input('Digite uma palavra ou nome da task: ')

                for task in tasks.findall('task'):
                    task_name = task.findtext('name')
                    if task_name_part.lower() in task_name.lower():  # Verifica se a palavra está no nome da tarefa
                        task_id = task.get('id')
                        print(f"Tarefa encontrada: {task_name} (ID: {task_id})")
                        break
                    
                if not task_id:
                    raise Exception(f"Nenhuma tarefa encontrada com a palavra '{task_name_part}' no nome.")

                # Obtendo os reports dessa tarefa
                reports = gmp.get_reports(filter_string=f"{task_id}")
                
                for report in reports.findall('report'):
                    report_id = report.get('id')
                    print(f"Report encontrado: {report_id}")

                report_test = gmp.get_report(report_id=report_id, report_format_id='a994b278-1f62-11e1-96ac-406186ea4fc5', filter_id='38c591ea-72fc-4dd3-a08c-9beb46968226')
                
                xml_string = ET.tostring(report_test, encoding="utf-8").decode()
                print("\n--- XML do Report ---\n")
                print(xml_string)
               

                
                    
        
            except Exception as e:
                print(f"Erro: {e}")
            
      
        
if __name__ == "__main__":
    report_test = Report_Manager()
    report_test.report()