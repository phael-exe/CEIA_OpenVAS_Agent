from gvm.connections import TLSConnection
from gvm.protocols.gmp import Gmp
from gvm.transforms import EtreeCheckCommandTransform
from gvm.xml import pretty_print


hostname = "127.0.0.1"
port = 9390

username = "admin"
password = "admin"

try:

    connection = TLSConnection(hostname=hostname, port=port)
    transform = EtreeCheckCommandTransform()

    print(f"Conectando ao gvmd em {hostname}:{port}...")

    with Gmp(connection=connection, transform=transform) as gmp:

        gmp.authenticate(username=username, password=password)

        version_response = gmp.get_version()

        print("Conexão bem sucedida!")
        print("Versão do GMP:")
        pretty_print(version_response)

except Exception as e:
    print(f"Erro de conexão: {e}")