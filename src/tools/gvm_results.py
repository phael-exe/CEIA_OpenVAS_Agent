import os
import re
import xml.etree.ElementTree as ET
from gvm.connections import UnixSocketConnection
from gvm.protocols.gmp import GMP
from gvm.transforms import EtreeCheckCommandTransform
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

path = os.getenv('GVMD_SOCKET_PATH')
username = os.getenv('GVMD_USERNAME')
password = os.getenv('GVMD_PASSWORD')

# Configuração da conexão com OpenVAS
connection = UnixSocketConnection(path=path)
transform = EtreeCheckCommandTransform()

class ResultManager:
    def __init__(self):
        pass
        
    def result(self):
        with GMP(connection=connection, transform=transform) as gmp:
            try:
                gmp.authenticate(username=username, password=password)
                tasks = gmp.get_tasks()

                task_id = None
                task_status = None
                task_name_input = input('\nType a word or the task name: ').strip().lower()
        
                # Buscar a tarefa pelo nome exato
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
                    print(f"\nNo task found with the name '{task_name_input}'.")
                    return None
                
                if task_status != "Done":
                    print(f"\nTask '{task_name}' is still running. Current status: {task_status}.\n")
                    return None
        
                results = gmp.get_results(task_id=task_id, filter_id='5ff29513-7ffb-460d-988c-536754c3a07a')
                result_str = ET.tostring(results, encoding="unicode", method="xml")

                # Chamar função para extrair os dados relevantes
                extracted_data = self.extract_multiple_results(result_str)
                return extracted_data

            except Exception as e:
                print(f"Error: {e}")
                return None
    
    def extract_multiple_results(self, xml_data: str) -> list:
        """Aplica regex para extrair todos os <result> e retorna uma lista simplificada"""
        pattern = re.compile(
            r'<result id="([^"]+)">.*?<name>(.*?)</name>.*?<host>(.*?)</host>.*?'
            r'<port>(.*?)</port>.*?<cvss_base>(.*?)</cvss_base>.*?'
            r'<solution[^>]*>(.*?)</solution>.*?<refs>(.*?)</refs>.*?'
            r'<threat>(.*?)</threat>.*?<description>(.*?)</description>',
            re.DOTALL
        )

        results_list = []
        matches = pattern.findall(xml_data)

        for match in matches:
            result_data = {
                "id": match[0],
                "name": match[1],
                "host": match[2],
                "port": match[3],
                "cvss_base": match[4],
                "solution": match[5],
                "refs": match[6],
                "threat": match[7],
                "description": match[8],
            }
            results_list.append(result_data)

        return results_list

def summarize_vulnerabilities(results_list):
    """Transforma a lista de vulnerabilidades em um resumo compacto"""
    summaries = []
    
    for result in results_list:
        summary = (f"[{result['threat'].upper()}] {result['name']} (CVSS {result['cvss_base']}) "
                   f"detected on {result['host']}:{result['port']}. "
                   f"Solution: {result['solution'][:1000]}")  # Limita a solução para evitar excesso de texto
        
        summaries.append(summary)
    
    return summaries

if __name__ == "__main__":
    sla = ResultManager()
    resultados = sla.result()

    if resultados:
        summaries = summarize_vulnerabilities(resultados)

        print("\n=== Compact Vulnerability Report ===")
        for summary in summaries:
            print(summary)
