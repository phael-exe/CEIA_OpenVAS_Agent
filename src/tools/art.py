from pyfiglet import Figlet
from colorama import Fore, Style

# Função para gerar a arte ASCII
def art_generation(texto, font='standard'):
    fig = Figlet(font=font)
    art = fig.renderText(texto)
    return art

# Função principal
def art_main():
    # Texto da arte
    art_text = "OPENVAS AGENT"

    # Gerar a arte ASCII
    art = art_generation(art_text, font='slant')  # Escolha a fonte que preferir

    # Exibir a arte com cores
    print(Fore.GREEN + art + Style.RESET_ALL)

    # Texto explicativo
    description = (
"""OpenVAS Agent is an AI tool that integrates with OpenVAS to automate tasks and provide actionable insights for vulnerability management. 
It simplifies reporting and helps prioritize remediation efforts efficiently."""    )

    # Exibir a descrição em azul
    print(Fore.RED + description + Style.RESET_ALL)

# Executar o script
if __name__ == "__main__":
    art_main()