
import re
import xml.etree.ElementTree as ET


# ============================================================
# CONVERTER VALOR
# ============================================================

def converter_valor(valor):

    if not valor:
        return 0.0

    valor = str(valor).strip()

    try:

        # Formato brasileiro: 1.234,56
        if ',' in valor:

            valor = valor.replace('.', '')
            valor = valor.replace(',', '.')

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

    restante = texto[match.end():]

    # Onde normalmente termina o nome
    fim = re.search(
        r'\b(CRM|CPF|CNPJ|CID|RG|RQE)\b',
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

    if not nome:
        return ''

    # Normaliza o título
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
# OBTER TEXTO
# ============================================================

def obter_texto(elemento):

    if elemento is None:
        return ''

    if elemento.text:
        return elemento.text.strip()

    return ''


# ============================================================
# OBTER VALOR
# ============================================================

def obter_valor(elemento):

    return converter_valor(
        obter_texto(elemento)
    )


# ============================================================
# LER UM XML DO PORTAL NACIONAL
# ============================================================

def ler_arquivo_nacional(caminho_arquivo):

    tree = ET.parse(caminho_arquivo)

    root = tree.getroot()

    # Namespace do Portal Nacional
    ns = {
        'nfse': 'http://www.sped.fazenda.gov.br/nfse'
    }

    # --------------------------------------------------------
    # NFS-e
    # --------------------------------------------------------

    numero_elem = root.find(
        './/nfse:infNFSe/nfse:nNFSe',
        ns
    )

    numero_nf = obter_texto(
        numero_elem
    )


    # --------------------------------------------------------
    # Data
    # --------------------------------------------------------

    data_elem = root.find(
        './/nfse:infDPS/nfse:dhEmi',
        ns
    )

    data_emissao = obter_texto(
        data_elem
    )

    if not data_emissao:

        data_elem = root.find(
            './/nfse:infNFSe/nfse:dhProc',
            ns
        )

        data_emissao = obter_texto(
            data_elem
        )


    # --------------------------------------------------------
    # PRESTADOR
    # --------------------------------------------------------

    prestador_elem = root.find(
        './/nfse:infNFSe/nfse:emit/nfse:xNome',
        ns
    )

    prestador = obter_texto(
        prestador_elem
    )


    # --------------------------------------------------------
    # TOMADOR
    # --------------------------------------------------------

    tomador_elem = root.find(
        './/nfse:infDPS/nfse:toma/nfse:xNome',
        ns
    )

    tomador = obter_texto(
        tomador_elem
    )


    # --------------------------------------------------------
    # MUNICÍPIO E UF
    # --------------------------------------------------------

    municipio_elem = root.find(
        './/nfse:infNFSe/nfse:emit/nfse:enderNac/nfse:cMun',
        ns
    )

    municipio = obter_texto(
        municipio_elem
    )


    uf_elem = root.find(
        './/nfse:infNFSe/nfse:emit/nfse:enderNac/nfse:UF',
        ns
    )

    uf = obter_texto(
        uf_elem
    )


    # --------------------------------------------------------
    # VALORES
    # --------------------------------------------------------

    valor_elem = root.find(
        './/nfse:infDPS/nfse:valores/nfse:vServPrest/nfse:vServ',
        ns
    )

    valor_total = obter_valor(
        valor_elem
    )


    iss_elem = root.find(
        './/nfse:infNFSe/nfse:valores/nfse:vISSQN',
        ns
    )

    valor_iss = obter_valor(
        iss_elem
    )


    # --------------------------------------------------------
    # PIS
    # --------------------------------------------------------

    pis_elem = root.find(
        './/nfse:piscofins/nfse:vPis',
        ns
    )

    valor_pis = obter_valor(
        pis_elem
    )


    # --------------------------------------------------------
    # COFINS
    # --------------------------------------------------------

    cofins_elem = root.find(
        './/nfse:piscofins/nfse:vCofins',
        ns
    )

    valor_cofins = obter_valor(
        cofins_elem
    )


    # --------------------------------------------------------
    # CSLL
    # --------------------------------------------------------

    csll_elem = root.find(
        './/nfse:CSLL',
        ns
    )

    valor_csll = obter_valor(
        csll_elem
    )


    # --------------------------------------------------------
    # IR
    # --------------------------------------------------------

    ir_elem = root.find(
        './/nfse:IR',
        ns
    )

    valor_ir = obter_valor(
        ir_elem
    )


    # --------------------------------------------------------
    # INSS
    # --------------------------------------------------------

    inss_elem = root.find(
        './/nfse:INSS',
        ns
    )

    valor_inss = obter_valor(
        inss_elem
    )


    # --------------------------------------------------------
    # DISCRIMINAÇÃO
    # --------------------------------------------------------

    discriminacao_elem = root.find(
        './/nfse:infDPS/nfse:serv/nfse:cServ/nfse:xDescServ',
        ns
    )

    discriminacao = obter_texto(
        discriminacao_elem
    )


    # --------------------------------------------------------
    # MÉDICO
    # --------------------------------------------------------

    medico = extrair_nome_medico(
        discriminacao
    )


    # --------------------------------------------------------
    # IMPOSTOS
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # RETORNO
    # --------------------------------------------------------

    nota = {

        'Prestador': prestador,

        'DataEmissao': data_emissao,

        'NumeroNF': numero_nf,

        'TomadorServico': tomador,

        'ValorTotal': valor_total,

        'TotalImpostos': total_impostos,

        'ValorIr': valor_ir,

        'ValorInss': valor_inss,

        'ValorIss': valor_iss,

        'SomaPisCofinsCsll':
            soma_pis_cofins_csll,

        'ValorPis': valor_pis,

        'ValorCofins': valor_cofins,

        'ValorCsll': valor_csll,

        'Medico': medico,

        'Municipio': municipio,

        'UF': uf,

        'Discriminacao': discriminacao,
    }

    return [nota]


# ============================================================
# LER VÁRIOS ARQUIVOS
# ============================================================

def ler_todos_os_nacionais(arquivos):

    todas_as_notas = []

    for arquivo in arquivos:

        notas = ler_arquivo_nacional(
            arquivo
        )

        todas_as_notas.extend(
            notas
        )

    return todas_as_notas


# ============================================================
# TESTE
# ============================================================

if __name__ == '__main__':

    import tkinter as tk
    from tkinter import filedialog


    root = tk.Tk()

    root.withdraw()

    root.attributes(
        '-topmost',
        True
    )


    arquivos = filedialog.askopenfilenames(

        title='Selecione os arquivos do Portal Nacional',

        filetypes=[

            (
                'XML',
                '*.xml'
            ),

            (
                'Todos os arquivos',
                '*.*'
            )

        ]

    )


    root.destroy()


    if not arquivos:

        print(
            'Nenhum arquivo selecionado.'
        )

        raise SystemExit


    notas = ler_todos_os_nacionais(
        arquivos
    )


    print()

    print('=' * 70)

    print('LEITOR PORTAL NACIONAL')

    print('=' * 70)

    print()

    print(
        f'Arquivos: {len(arquivos)}'
    )

    print(
        f'Notas encontradas: {len(notas)}'
    )

    print()


    for nota in notas:

        print('-' * 70)

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
            f"INSS: R$ {nota['ValorInss']:.2f}"
        )

        print(
            f"Médico: {nota['Medico']}"
        )


    print()

    print('=' * 70)

    print('TESTE FINALIZADO')

    print('=' * 70)
