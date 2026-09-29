import re
import xml.etree.ElementTree as ET



# ============================================================
# CONVERTER VALOR
# ============================================================

def converter_valor(valor):
    if valor is None or valor == '':
        return 0.0

    try:
        valor = str(valor).strip()

        # Formato brasileiro
        if ',' in valor:
            valor = valor.replace('.', '').replace(',', '.')

        return float(valor)

    except (ValueError, TypeError):
        return 0.0


# ============================================================
# EXTRAIR NOME DO MÉDICO
# ============================================================

def extrair_nome_medico(texto):

    if not texto:
        return ''

    texto = ' '.join(texto.split())

    # Identifica o título como uma palavra isolada,
    # com separação antes e depois.
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

    # Tudo que vem depois do título
    restante = texto[match.end():]

    # Define onde o nome termina
    fim = re.search(
        r'\b(CRM|CPF|CNPJ|CID|RG|RQE)\b',
        restante,
        re.IGNORECASE
    )

    if fim:
        nome = restante[:fim.start()]
    else:
        nome = restante

    nome = nome.strip(' -:;,./|')

    if not nome:
        return ''

    # Normaliza o título
    if titulo.upper().startswith('DRA') or titulo.upper() == 'DOUTORA':
        titulo_final = 'Dra.'
    else:
        titulo_final = 'Dr.'

    return f'{titulo_final} {nome}'

# ============================================================
# PEGAR TEXTO DE UM ELEMENTO
# ============================================================

def obter_texto(elemento, nome):
    if elemento is None:
        return ''

    for filho in elemento.iter():

        tag = filho.tag.split('}')[-1]

        if tag == nome:
            return (filho.text or '').strip()

    return ''


# ============================================================
# PEGAR VALOR
# ============================================================

def obter_valor(elemento, nome):
    return converter_valor(
        obter_texto(elemento, nome)
    )


# ============================================================
# LER UM ARQUIVO GISS
# ============================================================

def ler_arquivo_giss(caminho):
    try:

        tree = ET.parse(caminho)
        root = tree.getroot()

        notas = []

        # ====================================================
        # LOCALIZAR NFSE
        # ====================================================

        nfse = None

        for elemento in root.iter():

            nome = elemento.tag.split('}')[-1]

            if nome == 'Nfse':
                nfse = elemento
                break

        if nfse is None:
            return []

        # ====================================================
        # LOCALIZAR INFNFSE
        # ====================================================

        inf_nfse = None

        for elemento in nfse.iter():

            nome = elemento.tag.split('}')[-1]

            if nome == 'InfNfse':
                inf_nfse = elemento
                break

        if inf_nfse is None:
            return []

        # ====================================================
        # DADOS PRINCIPAIS
        # ====================================================

        numero = obter_texto(inf_nfse, 'Numero')

        data_emissao = obter_texto(
            inf_nfse,
            'DataEmissao'
        )

        # ====================================================
        # PRESTADOR
        # ====================================================

        prestador = None

        for elemento in inf_nfse.iter():

            nome = elemento.tag.split('}')[-1]

            if nome == 'PrestadorServico':
                prestador = elemento
                break

        nome_prestador = obter_texto(
            prestador,
            'RazaoSocial'
        )

        # ====================================================
        # TOMADOR
        # ====================================================

        tomador = None

        for elemento in inf_nfse.iter():

            nome = elemento.tag.split('}')[-1]

            if nome == 'TomadorServico':
                tomador = elemento
                break

        nome_tomador = obter_texto(
            tomador,
            'RazaoSocial'
        )

        # ====================================================
        # UF
        # ====================================================

        uf = obter_texto(
            prestador,
            'Uf'
        )

        # ====================================================
        # DECLARACAO
        # ====================================================

        declaracao = None

        for elemento in inf_nfse.iter():

            nome = elemento.tag.split('}')[-1]

            if nome == 'InfDeclaracaoPrestacaoServico':
                declaracao = elemento
                break

        # ====================================================
        # SERVICO
        # ====================================================

        servico = None

        if declaracao is not None:

            for elemento in declaracao.iter():

                nome = elemento.tag.split('}')[-1]

                if nome == 'Servico':
                    servico = elemento
                    break

        # ====================================================
        # VALORES
        # ====================================================

        valores = None

        if servico is not None:

            for elemento in servico.iter():

                nome = elemento.tag.split('}')[-1]

                if nome == 'Valores':
                    valores = elemento
                    break

        # ====================================================
        # VALORES DOS IMPOSTOS
        # ====================================================

        valor_total = obter_valor(
            valores,
            'ValorServicos'
        )

        valor_iss = obter_valor(
            valores,
            'ValorIss'
        )

        valor_inss = obter_valor(
            valores,
            'ValorInss'
        )

        valor_ir = obter_valor(
            valores,
            'ValorIr'
        )

        valor_csll = obter_valor(
            valores,
            'ValorCsll'
        )

        # ====================================================
        # PIS / COFINS
        # ====================================================

        valor_pis = obter_valor(
            valores,
            'vPis'
        )

        valor_cofins = obter_valor(
            valores,
            'vCofins'
        )

        soma_pis_cofins_csll = (
            valor_pis
            + valor_cofins
            + valor_csll
        )

        total_impostos = (
            valor_iss
            + valor_inss
            + valor_ir
            + valor_csll
            + valor_pis
            + valor_cofins
        )

        # ====================================================
        # DISCRIMINAÇÃO
        # ====================================================

        discriminacao = obter_texto(
            servico,
            'Discriminacao'
        )

        medico = extrair_nome_medico(
            discriminacao
        )

        # ====================================================
        # MUNICÍPIO
        # ====================================================

        municipio = obter_texto(
            servico,
            'CodigoMunicipio'
        )

        # ====================================================
        # RESULTADO PADRONIZADO
        # ====================================================

        nota = {
            'Prestador': nome_prestador,
            'DataEmissao': data_emissao,
            'NumeroNF': numero,
            'TomadorServico': nome_tomador,
            'ValorTotal': valor_total,
            'TotalImpostos': total_impostos,
            'ValorIr': valor_ir,
            'ValorInss': valor_inss,
            'ValorIss': valor_iss,
            'SomaPisCofinsCsll': soma_pis_cofins_csll,
            'ValorPis': valor_pis,
            'ValorCofins': valor_cofins,
            'ValorCsll': valor_csll,
            'Medico': medico,
            'Municipio': municipio,
            'UF': uf,
            'Discriminacao': discriminacao
        }

        notas.append(nota)

        return notas

    except Exception as erro:

        print(
            f"Erro ao ler o arquivo GISS "
            f"{caminho}: {erro}"
        )

        return []


# ============================================================
# LER VÁRIOS ARQUIVOS GISS
# ============================================================

def ler_todos_os_giss(arquivos):
    todas_as_notas = []

    for arquivo in arquivos:

        notas = ler_arquivo_giss(
            arquivo
        )

        todas_as_notas.extend(
            notas
        )

    return todas_as_notas