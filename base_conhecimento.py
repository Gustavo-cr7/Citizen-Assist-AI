from orientacao import Orientacao

ACENTOS = {
    "á": "a", "à": "a", "ã": "a", "â": "a",
    "é": "e", "ê": "e",
    "í": "i",
    "ó": "o", "õ": "o", "ô": "o",
    "ú": "u", "ü": "u",
    "ç": "c"
}

# Palavras muito comuns em perguntas que não indicam o assunto.
# São ignoradas na regra de +1 ponto (palavra da pergunta no título),
# evitando alternativas sem relação (ex.: "como" no título "Como funciona...").
PALAVRAS_IGNORADAS = [
    "como", "onde", "para", "qual", "quais", "quando", "quem", "quero",
    "preciso", "posso", "pode", "tenho", "minha", "meus", "minhas",
    "sobre", "isso", "esse", "essa", "este", "esta", "pelo", "pela",
]


def normalizar(texto):
    texto = str(texto).lower().strip()
    for letra, troca in ACENTOS.items():
        texto = texto.replace(letra, troca)
    for sinal in "?!.,;:()/-":
        texto = texto.replace(sinal, " ")
    return " " + " ".join(texto.split()) + " "


class BaseConhecimento:
    def __init__(self, caminho):
        self.caminho = caminho
        self.orientacoes = []

    def carregar(self):
        self.orientacoes = []

        try:
            arquivo = open(self.caminho, "r", encoding="utf-8")
            linhas = arquivo.readlines()
            arquivo.close()
        except FileNotFoundError:
            print(f"\n[Aviso] Arquivo '{self.caminho}' não encontrado.")
            return False
        except Exception as erro:
            print(f"\n[Aviso] Erro ao ler o arquivo '{self.caminho}': {erro}")
            return False

        for indice, linha in enumerate(linhas):
            linha_limpa = linha.strip()
            if not linha_limpa:
                continue

            if indice == 0 and linha_limpa.lower().startswith("id;categoria;"):
                continue

            campos = linha_limpa.split(";")
            if len(campos) != 9:
                print(f"[Aviso] Linha {indice + 1} ignorada por formato inválido.")
                continue

            palavras_chave_lista = [item.strip() for item in campos[3].split("|") if item.strip()]
            documentos_lista = [item.strip() for item in campos[5].split("|") if item.strip()]

            registro = {
                "id": campos[0].strip(),
                "categoria": campos[1].strip(),
                "titulo": campos[2].strip(),
                "palavras_chave": palavras_chave_lista,
                "resposta": campos[4].strip(),
                "documentos": documentos_lista,
                "onde": campos[6].strip(),
                "fonte": campos[7].strip(),
                "verificado_em": campos[8].strip(),
            }

            nova_orientacao = Orientacao(
                registro["id"],
                registro["categoria"],
                registro["titulo"],
                registro["palavras_chave"],
                registro["resposta"],
                registro["documentos"],
                registro["onde"],
                registro["fonte"],
                registro["verificado_em"],
            )
            self.orientacoes.append(nova_orientacao)

        return len(self.orientacoes) > 0

    def categorias(self):
        lista_categorias = []
        for orientacao in self.orientacoes:
            if orientacao.categoria not in lista_categorias:
                lista_categorias.append(orientacao.categoria)
        return lista_categorias

    def por_categoria(self, categoria_escolhida):
        resultado = []
        for orientacao in self.orientacoes:
            if normalizar(orientacao.categoria) == normalizar(categoria_escolhida):
                resultado.append(orientacao)
        return resultado

    def pontuar(self, pergunta, orientacao):
        pergunta_norm = normalizar(pergunta)
        titulo_norm = normalizar(orientacao.titulo)
        pontos = 0

        for chave in orientacao.palavras_chave:
            chave_norm = normalizar(chave)
            if chave_norm.strip() and chave_norm in pergunta_norm:
                pontos += 3

        palavras_pergunta = []
        for palavra in pergunta_norm.split():
            if len(palavra) >= 4 and palavra not in PALAVRAS_IGNORADAS and palavra not in palavras_pergunta:
                palavras_pergunta.append(palavra)

        for palavra in palavras_pergunta:
            if f" {palavra} " in titulo_norm:
                pontos += 1

        return pontos

    def buscar(self, pergunta):
        resultados = []
        for orientacao in self.orientacoes:
            pontos = self.pontuar(pergunta, orientacao)
            if pontos > 0:
                resultados.append((pontos, orientacao))

        resultados.sort(key=lambda item: item[0], reverse=True)
        return resultados
