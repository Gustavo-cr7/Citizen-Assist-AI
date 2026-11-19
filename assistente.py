import time
from datetime import datetime


class Assistente:
    def __init__(self, nome, base):
        self.nome = nome
        self.base = base
        self.historico = []
        self.notas_facilidade = []

    def perguntar(self):
        tentativas = 0
        inicio = time.time()

        while True:
            pergunta = input("\nDigite sua dúvida (0 para voltar): ").strip()

            if pergunta == "0":
                return

            if not pergunta:
                print("Atenção: digite uma pergunta válida ou 0 para voltar.")
                continue

            digitos = sum(1 for c in pergunta if c.isdigit())
            if digitos >= 8 or "@" in pergunta:
                print("Atenção: não digite CPF, telefone ou e-mail. Reescreva.")
                continue

            tentativas += 1
            resultados = self.base.buscar(pergunta)

            if not resultados or resultados[0][0] < 3:
                tempo_gasto = round(time.time() - inicio, 1)
                print("\nNão encontrei uma orientação para essa dúvida.")
                print("Sugestão: tente usar outras palavras ou consulte as categorias:", ", ".join(self.base.categorias()))
                self.registrar("pergunta", pergunta, "nenhum", "n", "n", tentativas, tempo_gasto)

                while True:
                    outra = input("\nVocê tem outra pergunta? (s/n): ").strip().lower()
                    if outra in ("s", "n"):
                        break
                    print("Entrada inválida. Digite apenas 's' ou 'n'.")

                if outra == "s":
                    # Não zera tentativas nem o tempo: a reformulação conta como
                    # nova tentativa do mesmo atendimento, até encontrar a resposta.
                    continue
                return

            melhor_pontuacao, melhor_orientacao = resultados[0]

            if melhor_pontuacao >= 6:
                confianca = "ALTA"
            else:
                confianca = "MÉDIA"

            print(f"\nConfiança da resposta: {confianca} ({melhor_pontuacao} pontos)")
            melhor_orientacao.exibir()

            alternativas = resultados[1:3]
            if alternativas:
                print("\nOutras orientações relacionadas:")
                for idx, (pts_alt, ori_alt) in enumerate(alternativas, start=1):
                    print(f"  {idx}. {ori_alt.titulo} [{ori_alt.categoria}] ({pts_alt} ponto(s))")

            while True:
                respondeu = input("\nEssa orientação respondeu sua dúvida? (s/n): ").strip().lower()
                if respondeu in ("s", "n"):
                    break
                print("Entrada inválida. Digite apenas 's' ou 'n'.")

            tempo_gasto = round(time.time() - inicio, 1)
            self.registrar("pergunta", pergunta, melhor_orientacao.id, "s", respondeu, tentativas, tempo_gasto)

            while True:
                outra = input("\nVocê tem outra pergunta? (s/n): ").strip().lower()
                if outra in ("s", "n"):
                    break
                print("Entrada inválida. Digite apenas 's' ou 'n'.")

            if outra == "s":
                tentativas = 0
                inicio = time.time()
                continue
            return

    def navegar(self):
        categorias = self.base.categorias()
        if not categorias:
            print("\nNenhuma categoria disponível.")
            return

        inicio = time.time()
        tentativas = 0

        while True:
            print("\n=== CATEGORIAS ===")
            for i, cat in enumerate(categorias, start=1):
                print(f"{i} - {cat}")
            print("0 - Voltar")

            opcao_cat = input("Escolha uma categoria (0 para voltar): ").strip()
            if opcao_cat == "0":
                return

            if not opcao_cat.isdigit() or not (1 <= int(opcao_cat) <= len(categorias)):
                print("Opção inválida!")
                continue

            categoria_selecionada = categorias[int(opcao_cat) - 1]
            orientacoes_cat = self.base.por_categoria(categoria_selecionada)

            while True:
                print(f"\n=== ORIENTAÇÕES: {categoria_selecionada} ===")
                for j, ori in enumerate(orientacoes_cat, start=1):
                    print(f"{j} - {ori.titulo}")
                print("0 - Voltar")

                opcao_ori = input("Escolha uma orientação (0 para voltar): ").strip()
                if opcao_ori == "0":
                    break

                if not opcao_ori.isdigit() or not (1 <= int(opcao_ori) <= len(orientacoes_cat)):
                    print("Opção inválida!")
                    continue

                tentativas += 1
                orientacao_escolhida = orientacoes_cat[int(opcao_ori) - 1]
                orientacao_escolhida.exibir()

                while True:
                    respondeu = input("\nEssa orientação respondeu sua dúvida? (s/n): ").strip().lower()
                    if respondeu in ("s", "n"):
                        break
                    print("Entrada inválida. Digite apenas 's' ou 'n'.")

                tempo_gasto = round(time.time() - inicio, 1)
                self.registrar(
                    "categoria",
                    orientacao_escolhida.titulo,
                    orientacao_escolhida.id,
                    "s",
                    respondeu,
                    tentativas,
                    tempo_gasto,
                )

                while True:
                    outra = input("\nVocê tem outra dúvida nas categorias? (s/n): ").strip().lower()
                    if outra in ("s", "n"):
                        break
                    print("Entrada inválida. Digite apenas 's' ou 'n'.")

                if outra == "s":
                    tentativas = 0
                    inicio = time.time()
                    break
                return

    def registrar(self, origem, pergunta, id_orientacao, encontrou, ajudou, tentativas, tempo):
        pergunta_limpa = pergunta.replace(";", ",").strip()
        data_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        atendimento = {
            "data": data_atual,
            "origem": origem,
            "pergunta": pergunta_limpa,
            "id_orientacao": str(id_orientacao),
            "encontrou": encontrou,
            "ajudou": ajudou,
            "tentativas": int(tentativas),
            "tempo": float(tempo),
        }
        self.historico.append(atendimento)

        try:
            arquivo = open("data/historico.csv", "a", encoding="utf-8")
            linha = (
                f"{atendimento['data']};"
                f"{atendimento['origem']};"
                f"{atendimento['pergunta']};"
                f"{atendimento['id_orientacao']};"
                f"{atendimento['encontrou']};"
                f"{atendimento['ajudou']};"
                f"{atendimento['tentativas']};"
                f"{atendimento['tempo']}\n"
            )
            arquivo.write(linha)
            arquivo.close()
        except Exception as erro:
            print(f"[Aviso] Não foi possível salvar em data/historico.csv: {erro}")

    def indicadores(self):
        total = len(self.historico)
        print("\n=== INDICADORES DE ATENDIMENTO ===")

        if total == 0:
            print("Nenhum atendimento realizado nesta sessão.")
            return

        encontrados = [item for item in self.historico if item["encontrou"] == "s"]
        ajudaram = [item for item in self.historico if item["ajudou"] == "s"]
        tempos = [item["tempo"] for item in self.historico]
        tentativas_total = sum(item["tentativas"] for item in self.historico)

        perc_encontrada = round((len(encontrados) / total) * 100, 1)
        perc_ajudou = round((len(ajudaram) / total) * 100, 1)
        tempo_medio = round(sum(tempos) / total, 1)
        media_tentativas = round(tentativas_total / total, 1)

        if self.notas_facilidade:
            media_facilidade = round(sum(self.notas_facilidade) / len(self.notas_facilidade), 1)
        else:
            media_facilidade = "Sem avaliação"

        duvidas_sem_solucao = [
            item["pergunta"]
            for item in self.historico
            if item["encontrou"] == "n" or item["ajudou"] == "n"
        ]

        print(f"Resposta encontrada (%)    : {perc_encontrada}%")
        print(f"Taxa de acerto: ajudou (%) : {perc_ajudou}%")
        print(f"Tempo médio para encontrar : {tempo_medio}s")
        print(f"Tentativas por atendimento : {media_tentativas}")
        print(f"Facilidade de uso (1 a 5)  : {media_facilidade}")
        print("Lista de dúvidas sem solução:")
        if duvidas_sem_solucao:
            for duvida in duvidas_sem_solucao:
                print(f"  - {duvida}")
        else:
            print("  - Nenhuma")

    def exportar_csv(self):
        try:
            arquivo = open("data/atendimentos.csv", "w", encoding="utf-8")
            arquivo.write("data;origem;pergunta;id_orientacao;encontrou;ajudou;tentativas;tempo\n")
            for item in self.historico:
                linha = (
                    f"{item['data']};"
                    f"{item['origem']};"
                    f"{item['pergunta']};"
                    f"{item['id_orientacao']};"
                    f"{item['encontrou']};"
                    f"{item['ajudou']};"
                    f"{item['tentativas']};"
                    f"{item['tempo']}\n"
                )
                arquivo.write(linha)
            arquivo.close()
        except Exception as erro:
            print(f"[Aviso] Erro ao exportar CSV: {erro}")
