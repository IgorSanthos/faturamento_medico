
import xml.etree.ElementTree as ET

from leitor_nacional import ler_arquivo_nacional
from leitor_xml import extrair_dados_xml
from leitor_sao_paulo import extrair_dados_sao_paulo
from leitor_giss import ler_arquivo_giss


# ============================================================
# IDENTIFICAR FORMATO
# ============================================================

def identificar_formato(caminho_arquivo):

    # ========================================================
    # TENTA IDENTIFICAR XML
    # ========================================================

    try:

        tree = ET.parse(caminho_arquivo)

        root = tree.getroot()

        # ----------------------------------------------------
        # Namespace do XML
        # ----------------------------------------------------

        namespace = ''

        if root.tag.startswith('{'):

            namespace = root.tag.split('}')[0][1:]


        # ----------------------------------------------------
        # GISS
        # ----------------------------------------------------

        if 'giss.com.br' in namespace.lower():

            return 'GISS'


        # ----------------------------------------------------
        # GINFES
        # ----------------------------------------------------

        if 'ginfes.com.br' in namespace.lower():

            return 'GINFES'

        # ----------------------------------------------------
        # PORTAL NACIONAL
        # ----------------------------------------------------

        if 'sped.fazenda.gov.br/nfse' in namespace.lower():
            return 'PORTAL_NACIONAL'
        # ----------------------------------------------------
        # Segunda identificação pelas tags
        # ----------------------------------------------------

        tags = set()

        for elemento in root.iter():

            nome = elemento.tag.split('}')[-1]

            tags.add(nome)


        if (
            'InfNfse' in tags
            and
            'InfDeclaracaoPrestacaoServico' in tags
        ):

            return 'GISS'


        if (
            'IdentificacaoNfse' in tags
            and
            'PrestadorServico' in tags
            and
            'Servico' in tags
        ):

            return 'GINFES'


    except Exception:

        pass


    # ========================================================
    # SÃO PAULO
    # ========================================================

    try:

        with open(
            caminho_arquivo,
            'r',
            encoding='latin1'
        ) as arquivo:

            primeira_linha = arquivo.readline()


        if ';' in primeira_linha:

            return 'SAO_PAULO'


    except Exception:

        pass


    return 'DESCONHECIDO'


# ============================================================
# PROCESSAR ARQUIVOS
# ============================================================

def ler_arquivos(arquivos):

    """
    Regras:

    GISS:
        - permite vários arquivos.

    GINFES:
        - permite apenas um arquivo.

    SAO_PAULO:
        - permite apenas um arquivo.
    """

    if not arquivos:

        return []


    # ========================================================
    # IDENTIFICAR OS ARQUIVOS
    # ========================================================

    formatos = []

    for arquivo in arquivos:

        formato = identificar_formato(
            arquivo
        )

        formatos.append(
            formato
        )


    # ========================================================
    # NÃO PERMITIR FORMATOS DIFERENTES
    # ========================================================

    if len(set(formatos)) > 1:

        raise ValueError(
            'Não é permitido misturar arquivos '
            'de formatos diferentes.'
        )


    formato = formatos[0]


    # ========================================================
    # FORMATO DESCONHECIDO
    # ========================================================

    if formato == 'DESCONHECIDO':

        raise ValueError(
            'Não foi possível identificar '
            'o formato do arquivo.'
        )


    # ========================================================
    # GINFES
    # ========================================================

    if formato == 'GINFES':

        if len(arquivos) > 1:

            raise ValueError(
                'O formato Ginfes permite '
                'apenas um arquivo por vez.'
            )


        return extrair_dados_xml(
            arquivos[0]
        )


    # ========================================================
    # SÃO PAULO
    # ========================================================

    if formato == 'SAO_PAULO':

        if len(arquivos) > 1:

            raise ValueError(
                'O formato São Paulo permite '
                'apenas um arquivo por vez.'
            )


        return extrair_dados_sao_paulo(
            arquivos[0]
        )


    # ========================================================
    # GISS
    # ========================================================

    if formato == 'GISS':

        todas_as_notas = []


        for arquivo in arquivos:

            notas = ler_arquivo_giss(
                arquivo
            )

            todas_as_notas.extend(
                notas
            )


        return todas_as_notas

    # ========================================================
    # PORTAL NACIONAL
    # ========================================================

    if formato == 'PORTAL_NACIONAL':

        todas_as_notas = []

        for arquivo in arquivos:

            notas = ler_arquivo_nacional(arquivo)

            todas_as_notas.extend(notas)

        return todas_as_notas

    return []


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

        title='Selecione os arquivos',

        filetypes=[

            (
                'Arquivos suportados',
                '*.xml *.csv *.txt'
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


    try:

        notas = ler_arquivos(
            list(arquivos)
        )


        print()

        print('=' * 70)

        print('LEITOR GERAL')

        print('=' * 70)

        print()

        print(
            f'Formato: '
            f'{identificar_formato(arquivos[0])}'
        )

        print(
            f'Arquivos: '
            f'{len(arquivos)}'
        )

        print(
            f'Notas encontradas: '
            f'{len(notas)}'
        )

        print()

        for nota in notas:

            print(
                '-' * 70
            )

            print(
                f"NFS-e: "
                f"{nota.get('NumeroNF', '')}"
            )

            print(
                f"Prestador: "
                f"{nota.get('Prestador', '')}"
            )

            print(
                f"Tomador: "
                f"{nota.get('TomadorServico', '')}"
            )

            print(
                f"Valor: "
                f"R$ {nota.get('ValorTotal', 0):.2f}"
            )

            print(
                f"UF: "
                f"{nota.get('UF', '')}"
            )

            print(
                f"Médico: "
                f"{nota.get('Medico', '')}"
            )


        print()

        print('=' * 70)

        print('TESTE FINALIZADO')

        print('=' * 70)


    except ValueError as erro:

        print()

        print(
            f'ERRO: {erro}'
        )


