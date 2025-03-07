import os
from gvm.connections import UnixSocketConnection
from gvm.protocols.gmp import GMP
from gvm.transforms import EtreeCheckCommandTransform
from dotenv import load_dotenv
import xml.etree.ElementTree as ET

load_dotenv()

path = os.getenv('GVMD_SOCKET_PATH')
username = os.getenv('GVMD_USERNAME')
password = os.getenv('GVMD_PASSWORD')

connection = UnixSocketConnection(path=path)
transform = EtreeCheckCommandTransform()

class ResultManager:
    def __init__(self):
        pass
        
    def result(self) -> str:
        with GMP(connection=connection, transform=transform) as gmp:
            try:

                gmp.authenticate(username=username, password=password)
        
                tasks = gmp.get_tasks()

            
                task_id = None
                task_status = None
                task_name_input = input('\nType a word or the task name: ').strip().lower()
        
                #Trocar lógica para buscar a tarefa que contém o nome exato desejado
                for task in tasks.findall('task'):
                    task_name_elem = task.find('name')
                    status_elem = task.find('status')

                    if task_name_elem is not None and status_elem is not None:
                        task_name = task_name_elem.text.strip().lower()
                        task_status = status_elem.text

                        if task_name == task_name_input:
                            task_id = task.get('id')
                            break

                if not task_id:
                    print()
                    raise ValueError(f"No task found with the word '{task_name_input}'.")
                
                if task_status != "Done":
                    print(f"\nIt is not possible to return the report yet, the task '{task_name}' is in status: {task_status}.\n")
                    return None
        
                results = gmp.get_results(task_id=task_id, filter_id='5ff29513-7ffb-460d-988c-536754c3a07a')
        
                result_str = ET.tostring(results, encoding="unicode", method="xml")
                return result_str
            
            except Exception as e:
                print(f"Error: {e}")
                return None
            
        
                
        
                

if __name__ == "__main__":
    sla = ResultManager()
    resultado = sla.result()
    if resultado:
        print(resultado)




