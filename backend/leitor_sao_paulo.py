import csv
import re


# ============================================================
# FORMATAÇÃO DE VALORES
# ============================================================

def converter_valor(valor):
    """
    Converte valores no padrão brasileiro para float.

    Exemplos:
        1.712,50 -> 1712.50
        34,25    -> 34.25
        0,00     -> 0.0
        vazio    -> 0.0
    """

    if valor is None:
        return 0.0

    valor = str(valor).strip()

    if not valor:
        return 0.0

    try:
        # Remove espaços
        valor = valor.replace(" ", "")

        # Formato brasileiro:
        # 1.234,56 -> 1234.56
        valor = valor.replace(".", "")
        valor = valor.replace(",", ".")

        return float(valor)

    except (ValueError, TypeError):
        return 0.0


# ============================================================
# IDENTIFICAÇÃO DO MÉDICO
# ============================================================


def extrair_nome_medico(texto):

    if not texto:
        return ''

    texto = ' '.join(texto.split())

    # ========================================================
    # IDENTIFICAR O TÍTULO
    # ========================================================

    padrao = re.compile(
        r'(?<!\w)'
        r'(DR|DRA|DRª|DOUTOR|DOUTORA)'
        r'\.?(?=\s|[.,:;-]|$)'
        r'\s+',
        re.IGNORECASE
    )

    match = padrao.search(texto)

    if not match:
        return ''

    titulo = match.group(1)

    restante = texto[match.end():]

    # ========================================================
    # MARCADORES QUE INDICAM O FIM DO NOME
    # ========================================================

    fim = re.search(
        r'\b('
        r'CRM|CPF|CNPJ|CID|RG|RQE|'
        r'LEI\s+DA\s+TRANSPAR[ÊE]NCIA|'
        r'TRIBUTOS?|'
        r'VALOR\s+APROXIMADO|'
        r'IMPOSTOS?|'
        r'CONFORME\s+TABELA|'
        r'IBPT'
        r')\b',
        restante,
        re.IGNORECASE
    )

    if fim:

        nome = restante[:fim.start()]

    else:

        nome = restante

    # ========================================================
    # LIMPAR FINAL DO NOME
    # ========================================================

    nome = nome.strip(
        ' -:;,./|'
    )

    # Remove separadores que possam ter ficado no final
    nome = re.sub(
        r'[\s|;,.:/-]+$',
        '',
        nome
    )

    if not nome:
        return ''

    # ========================================================
    # NORMALIZAR TÍTULO
    # ========================================================

    if (
        titulo.upper().startswith('DRA')
        or
        titulo.upper() == 'DOUTORA'
    ):

        titulo_final = 'Dra.'

    else:

        titulo_final = 'Dr.'

    return f'{titulo_final} {nome}'



# ============================================================
# LEITURA DO ARQUIVO
# ============================================================

def ler_arquivo_sao_paulo(caminho_arquivo):
    """
    Lê o arquivo de NFS-e de São Paulo.

    O arquivo possui:
        - cabeçalho separado por ;
        - registros separados por ;
        - valores no formato brasileiro.
    """

    notas_fiscais = []

    with open(
        caminho_arquivo,
        "r",
        encoding="latin1",
        newline=""
    ) as arquivo:

        leitor = csv.reader(
            arquivo,
            delimiter=";"
        )

        linhas = list(leitor)

    if not linhas:
        return []

    cabecalho = linhas[0]

    # Remove BOM caso exista
    if cabecalho:
        cabecalho[0] = cabecalho[0].replace("\ufeff", "")

    # Remove espaços desnecessários dos nomes das colunas
    cabecalho = [
        coluna.strip()
        for coluna in cabecalho
    ]

    # Cria mapa:
    # nome da coluna -> posição
    indices = {
        nome: indice
        for indice, nome in enumerate(cabecalho)
    }

    def obter_coluna(linha, nome_coluna):
        """
        Retorna o valor de uma coluna sem gerar erro
        caso a coluna não exista.
        """

        indice = indices.get(nome_coluna)

        if indice is None:
            return ""

        if indice >= len(linha):
            return ""

        return linha[indice].strip()

    # ========================================================
    # PROCESSAMENTO DAS NOTAS
    # ========================================================

    for linha in linhas[1:]:

        if not linha:
            continue

        # Ignora linha TOTAL
        tipo_registro = obter_coluna(
            linha,
            "Tipo de Registro"
        )

        if tipo_registro.lower() == "total":
            continue

        # ====================================================
        # DADOS PRINCIPAIS
        # ====================================================

        numero_nf = obter_coluna(
            linha,
            "Nº NFS-e"
        )

        data_emissao = obter_coluna(
            linha,
            "Data Hora NFE"
        )

        prestador = obter_coluna(
            linha,
            "Razão Social do Prestador"
        )

        tomador = obter_coluna(
            linha,
            "Razão Social do Tomador"
        )

        cidade = obter_coluna(
            linha,
            "Cidade do Prestador"
        )

        uf = obter_coluna(
            linha,
            "UF do Prestador"
        )

        # ====================================================
        # VALORES
        # ====================================================

        valor_total = converter_valor(
            obter_coluna(
                linha,
                "Valor dos Serviços"
            )
        )

        valor_iss = converter_valor(
            obter_coluna(
                linha,
                "ISS devido"
            )
        )

        valor_pis = converter_valor(
            obter_coluna(
                linha,
                "PIS/PASEP"
            )
        )

        valor_cofins = converter_valor(
            obter_coluna(
                linha,
                "COFINS"
            )
        )

        valor_inss = converter_valor(
            obter_coluna(
                linha,
                "INSS"
            )
        )

        valor_ir = converter_valor(
            obter_coluna(
                linha,
                "IR"
            )
        )

        valor_csll = converter_valor(
            obter_coluna(
                linha,
                "CSLL"
            )
        )

        # ====================================================
        # MÉDICO
        # ====================================================

        discriminacao = obter_coluna(
            linha,
            "Discriminação dos Serviços"
        )

        medico = extrair_nome_medico(
            discriminacao
        )

        # ====================================================
        # TOTAIS
        # ====================================================

        soma_pis_cofins_csll = round(
            valor_pis
            + valor_cofins
            + valor_csll,
            2
        )

        total_impostos = round(
            valor_iss
            + valor_inss
            + valor_pis
            + valor_cofins
            + valor_csll
            + valor_ir,
            2
        )

        # ====================================================
        # DICIONÁRIO PADRÃO DO SISTEMA
        # ====================================================

        nota = {
            "Prestador": prestador,
            "DataEmissao": data_emissao,
            "NumeroNF": numero_nf,
            "TomadorServico": tomador,

            "ValorTotal": valor_total,

            "TotalImpostos": total_impostos,

            "ValorIr": valor_ir,
            "ValorInss": valor_inss,
            "ValorIss": valor_iss,

            "SomaPisCofinsCsll": soma_pis_cofins_csll,

            "ValorPis": valor_pis,
            "ValorCofins": valor_cofins,
            "ValorCsll": valor_csll,

            "Medico": medico,

            # Informações adicionais
            "Municipio": cidade,
            "UF": uf,
            "Discriminacao": discriminacao,
        }

        notas_fiscais.append(nota)

    return notas_fiscais


# ============================================================
# FUNÇÃO PRINCIPAL
# ============================================================

def extrair_dados_sao_paulo(caminho_arquivo):
    """
    Função principal utilizada pelo sistema.

    Recebe o caminho do arquivo de São Paulo
    e retorna uma lista de notas.
    """

    return ler_arquivo_sao_paulo(
        caminho_arquivo
    )


# ============================================================
# TESTE DIRETO DO ARQUIVO
# ============================================================

if __name__ == "__main__":

    import tkinter as tk
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()

    caminho = filedialog.askopenfilename(
        title="Selecione o arquivo de São Paulo",
        filetypes=[
            ("Arquivos CSV/TXT", "*.csv *.txt"),
            ("Todos os arquivos", "*.*"),
        ],
    )

    root.destroy()

    if not caminho:
        print("Nenhum arquivo selecionado.")
        input("\nPressione ENTER para sair...")
        raise SystemExit

    notas = extrair_dados_sao_paulo(caminho)

    print()
    print("=" * 70)
    print("LEITOR SÃO PAULO")
    print("=" * 70)
    print()

    print(f"Notas encontradas: {len(notas)}")
    print()

    for nota in notas:

        print("-" * 70)

        print(
            f"NFS-e: {nota['NumeroNF']}"
        )

        print(
            f"Data: {nota['DataEmissao']}"
        )

        print(
            f"Prestador: {nota['Prestador']}"
        )

        print(
            f"Tomador: {nota['TomadorServico']}"
        )

        print(
            f"Município: {nota['Municipio']}"
        )

        print(
            f"UF: {nota['UF']}"
        )

        print(
            f"Valor: R$ {nota['ValorTotal']:.2f}"
        )

        print(
            f"ISS: R$ {nota['ValorIss']:.2f}"
        )

        print(
            f"INSS: R$ {nota['ValorInss']:.2f}"
        )

        print(
            f"PIS: R$ {nota['ValorPis']:.2f}"
        )

        print(
            f"COFINS: R$ {nota['ValorCofins']:.2f}"
        )

        print(
            f"CSLL: R$ {nota['ValorCsll']:.2f}"
        )

        print(
            f"IR: R$ {nota['ValorIr']:.2f}"
        )

        print(
            f"Médico: {nota['Medico']}"
        )

    print()
    print("=" * 70)
    print("TESTE FINALIZADO")
    print("=" * 70)

    input("\nPressione ENTER para sair...")