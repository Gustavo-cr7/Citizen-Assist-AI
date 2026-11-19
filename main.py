import os
from base_conhecimento import BaseConhecimento
from assistente import Assistente

os.chdir(os.path.dirname(os.path.abspath(__file__)))

base = BaseConhecimento("data/base_conhecimento.csv")
base.carregar()

assistente = Assistente("Citizen Assist AI", base)

while True:
    print(f"\n=== {assistente.nome} ===")
    print("1 - Fazer pergunta")
    print("2 - Navegar por categorias")
    print("3 - Ver indicadores")
    print("4 - Exportar atendimentos (CSV)")
    print("0 - Sair")

    opcao = input("Escolha uma opção: ").strip()

    if opcao == "1":
        base.carregar()
        assistente.perguntar()
    elif opcao == "2":
        base.carregar()
        assistente.navegar()
    elif opcao == "3":
        assistente.indicadores()
    elif opcao == "4":
        assistente.exportar_csv()
        print("Atendimentos exportados em data/atendimentos.csv!")
    elif opcao == "0":
        while True:
            nota = input("\nDe 1 a 5, qual nota você dá para a facilidade de uso do assistente? ").strip()
            if nota.isdigit() and 1 <= int(nota) <= 5:
                assistente.notas_facilidade.append(int(nota))
                break
            print("Nota inválida. Digite um número de 1 a 5.")

        assistente.indicadores()
        assistente.exportar_csv()
        print("Encerrando o programa. Até logo!")
        break
    else:
        print("Opção inválida! Digite um número de 0 a 4.")
