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
        valor = valor.replace(" ", "")
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
    # 1. PROCURAR MÉDICO COM TÍTULO
    # ========================================================

    padrao_titulo = re.compile(
        r'(?<!\w)'
        r'(DR|DRA|DRª|DOUTOR|DOUTORA)'
        r'\.?(?=\s|[.,:;-]|$)'
        r'\s+',
        re.IGNORECASE
    )

    match = padrao_titulo.search(texto)

    if match:

        titulo = match.group(1)

        restante = texto[match.end():]

        # ====================================================
        # MARCADORES QUE INDICAM O FIM DO NOME
        # ====================================================

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

        nome = nome.strip(
            ' -:;,./|'
        )

        nome = re.sub(
            r'[\s|;,.:/-]+$',
            '',
            nome
        )

        if not nome:
            return ''

        # ====================================================
        # PEGAR SOMENTE O PRIMEIRO NOME
        # ====================================================

        primeiro_nome = nome.split()[0]

        # ====================================================
        # NORMALIZAR TÍTULO
        # ====================================================

        if (
            titulo.upper().startswith('DRA')
            or
            titulo.upper() == 'DOUTORA'
        ):
            titulo_final = 'Dra.'
        else:
            titulo_final = 'Dr.'

        return f'{titulo_final} {primeiro_nome}'

    # ========================================================
    # 2. PROCURAR "PRESTADO POR"
    # ========================================================

    padrao_prestado_por = re.search(
        r'\bprestado\s+por\s+',
        texto,
        re.IGNORECASE
    )

    if not padrao_prestado_por:
        return ''

    restante = texto[
        padrao_prestado_por.end():
    ]

    # ========================================================
    # VERIFICAR SE EXISTE DR / DRA
    # ========================================================

    padrao_titulo_depois = re.match(
        r'(DR|DRA|DRª|DOUTOR|DOUTORA)'
        r'\.?(?=\s|[.,:;-]|$)'
        r'\s+',
        restante,
        re.IGNORECASE
    )

    if padrao_titulo_depois:

        titulo = padrao_titulo_depois.group(1)

        restante = restante[
            padrao_titulo_depois.end():
        ]

        if (
            titulo.upper().startswith('DRA')
            or
            titulo.upper() == 'DOUTORA'
        ):
            titulo_final = 'Dra.'
        else:
            titulo_final = 'Dr.'

    else:

        titulo_final = 'Dr.'

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

    nome = nome.strip(
        ' -:;,./|'
    )

    nome = re.sub(
        r'[\s|;,.:/-]+$',
        '',
        nome
    )

    if not nome:
        return ''

    # ========================================================
    # PEGAR SOMENTE O PRIMEIRO NOME
    # ========================================================

    primeiro_nome = nome.split()[0]

    return f'{titulo_final} {primeiro_nome}'


    # ========================================================
    # 2. PROCURAR "PRESTADO POR"
    # ========================================================

    padrao_prestado_por = re.search(
        r'\bprestado\s+por\s+',
        texto,
        re.IGNORECASE
    )

    if not padrao_prestado_por:
        return ''

    restante = texto[padrao_prestado_por.end():]

    # ========================================================
    # VERIFICAR SE DEPOIS DE "PRESTADO POR"
    # JÁ EXISTE DR / DRA
    # ========================================================

    padrao_titulo_depois = re.match(
        r'(DR|DRA|DRª|DOUTOR|DOUTORA)'
        r'\.?(?=\s|[.,:;-]|$)'
        r'\s+',
        restante,
        re.IGNORECASE
    )

    if padrao_titulo_depois:

        titulo = padrao_titulo_depois.group(1)

        restante = restante[
            padrao_titulo_depois.end():
        ]

        if (
            titulo.upper().startswith('DRA')
            or
            titulo.upper() == 'DOUTORA'
        ):
            titulo_final = 'Dra.'
        else:
            titulo_final = 'Dr.'

    else:

        # Se "prestado por" não tiver título,
        # considera-se médico e usa Dr.
        titulo_final = 'Dr.'

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
    # LIMPAR NOME
    # ========================================================

    nome = nome.strip(
        ' -:;,./|'
    )

    nome = re.sub(
        r'[\s|;,.:/-]+$',
        '',
        nome
    )

    if not nome:
        return ''

    return f'{titulo_final} {nome}'


# ============================================================
# LEITURA DO ARQUIVO
# ============================================================

def ler_arquivo_sao_paulo(caminho_arquivo):
    """
    Lê o arquivo de NFS-e de São Paulo.
    """
    notas_fiscais = []

    with open(caminho_arquivo, "r", encoding="latin1", newline="") as arquivo:
        leitor = csv.reader(arquivo, delimiter=";")
        linhas = list(leitor)

    if not linhas:
        return []

    cabecalho = linhas[0]

    if cabecalho:
        cabecalho[0] = cabecalho[0].replace("\ufeff", "")

    cabecalho = [coluna.strip() for coluna in cabecalho]

    indices = {
        nome: indice
        for indice, nome in enumerate(cabecalho)
    }

    def obter_coluna(linha, nome_coluna):
        indice = indices.get(nome_coluna)

        if indice is None or indice >= len(linha):
            return ""

        return linha[indice].strip()

    # ========================================================
    # PROCESSAMENTO DAS NOTAS
    # ========================================================

    for linha in linhas[1:]:
        if not linha:
            continue

        tipo_registro = obter_coluna(linha, "Tipo de Registro")
        if tipo_registro.lower() == "total":
            continue

        situacao_nota = obter_coluna(
            linha,
            "Situação da Nota Fiscal"
        ).strip().upper()

        # Aceita somente notas autorizadas ou canceladas
        if situacao_nota not in ("T", "C"):
            continue

        numero_nf = obter_coluna(linha, "Nº NFS-e")
        data_emissao = obter_coluna(linha, "Data Hora NFE")
        prestador = obter_coluna(linha, "Razão Social do Prestador")
        tomador = obter_coluna(linha, "Razão Social do Tomador")
        cidade = obter_coluna(linha, "Cidade do Prestador")
        uf = obter_coluna(linha, "UF do Prestador")

        valor_total = converter_valor(obter_coluna(linha, "Valor dos Serviços"))
        valor_iss = converter_valor(obter_coluna(linha, "ISS devido"))
        valor_pis = converter_valor(obter_coluna(linha, "PIS/PASEP"))
        valor_cofins = converter_valor(obter_coluna(linha, "COFINS"))
        valor_inss = converter_valor(obter_coluna(linha, "INSS"))
        valor_ir = converter_valor(obter_coluna(linha, "IR"))
        valor_csll = converter_valor(obter_coluna(linha, "CSLL"))

        discriminacao = obter_coluna(linha, "Discriminação dos Serviços")
        medico = extrair_nome_medico(discriminacao)

        if valor_csll > 0:
            valor_pcc_retido = round(valor_total * 0.0465, 2)
        else:
            valor_pcc_retido = 0.0

        soma_pis_cofins_csll = round(
            valor_pis + valor_cofins + valor_csll,
            2
        )

        total_impostos = round(
            valor_iss + valor_inss + valor_pis + valor_cofins + valor_csll + valor_ir,
            2
        )

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
            "ValorPisRetido": valor_pis,
            "ValorCofinsRetido": valor_cofins,
            "ValorCsllRetido": valor_csll,
            "ValorPccRetido": valor_pcc_retido,
            "TipoRetPisCofins": 0,
            "Medico": medico,
            "SituacaoNota": situacao_nota,
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
    """
    return ler_arquivo_sao_paulo(caminho_arquivo)


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
        print(f"NFS-e: {nota['NumeroNF']}")
        print(f"Data: {nota['DataEmissao']}")
        print(f"Prestador: {nota['Prestador']}")
        print(f"Tomador: {nota['TomadorServico']}")
        print(f"Município: {nota['Municipio']}")
        print(f"UF: {nota['UF']}")
        print(f"Valor: R$ {nota['ValorTotal']:.2f}")
        print(f"ISS: R$ {nota['ValorIss']:.2f}")
        print(f"INSS: R$ {nota['ValorInss']:.2f}")
        print(f"PIS: R$ {nota['ValorPis']:.2f}")
        print(f"COFINS: R$ {nota['ValorCofins']:.2f}")
        print(f"CSLL: R$ {nota['ValorCsll']:.2f}")
        print(f"PCC 4,65%: R$ {nota['ValorPccRetido']:.2f}")
        print(f"IR: R$ {nota['ValorIr']:.2f}")
        print(f"Médico: {nota['Medico']}")

    print()
    print("=" * 70)
    print("TESTE FINALIZADO")
    print("=" * 70)
    input("\nPressione ENTER para sair...")