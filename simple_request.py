from gvm.connections import UnixSocketConnection
from gvm.protocols.gmp import Gmp
from dotenv import load_dotenv
import os

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Obtém o caminho para o socket a partir da variável de ambiente
path = '/var/run/gvmd/gvmd.sock'

print(path is not None)

# Estabelece a conexão usando o caminho do socket
connection = UnixSocketConnection(path=path)

# Usando a declaração 'with' para conectar e desconectar automaticamente do gvmd
with Gmp(connection=connection) as gmp:
    # Obtém a mensagem de resposta retornada como uma string codificada em utf-8
    response = gmp.get_version()

    # Imprime a mensagem de resposta
    print(response)