import re
import xml.etree.ElementTree as ET
import tkinter as tk
from tkinter import filedialog

def extrair_nome_medico(texto):

    if not texto:
        return ''

    texto = ' '.join(texto.split())

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

    if (
        titulo.upper().startswith('DRA')
        or
        titulo.upper() == 'DOUTORA'
    ):
        titulo_final = 'Dra.'
    else:
        titulo_final = 'Dr.'

    return f'{titulo_final} {nome}'

def selecionar_arquivos_xml():
    """Abre uma janela de diálogo para o usuário selecionar um ou múltiplos arquivos XML."""
    root = tk.Tk()
    root.withdraw()  # Oculta a janela principal do Tkinter
    root.attributes('-topmost', True)  # Traz a janela para a frente

    caminhos_arquivos = filedialog.askopenfilenames(

    )
    
    root.destroy()
    return caminhos_arquivos

def extrair_dados_xml(caminho_arquivo):
    """Lê um arquivo XML de NFS-e (Ginfes/WSDL) e extrai todas as notas dentro dele."""
    tree = ET.parse(caminho_arquivo)
    root = tree.getroot()

    namespaces = {
        'ns2': 'http://www.w3.org/2000/09/xmldsig#',
        'ns3': 'http://www.ginfes.com.br/tipos',
    }

    notas_fiscais = []

    for nfse in root.findall('.//ns2:Nfse', namespaces):
        prestador_elem = nfse.find('ns3:PrestadorServico/ns3:RazaoSocial', namespaces)
        prestador = prestador_elem.text if prestador_elem is not None else ''

        data_emissao_elem = nfse.find('ns3:DataEmissao', namespaces)
        data_emissao = data_emissao_elem.text if data_emissao_elem is not None else ''

        numero_elem = nfse.find('ns3:IdentificacaoNfse/ns3:Numero', namespaces)
        numero_nf = numero_elem.text if numero_elem is not None else ''

        tomador_elem = nfse.find('ns3:TomadorServico/ns3:RazaoSocial', namespaces)
        tomador = tomador_elem.text if tomador_elem is not None else ''

        valores_elem = nfse.find('ns3:Servico/ns3:Valores', namespaces)

        # Função de busca flexível para ignorar variações de nomes de tags (vPis vs ValorPis)
        def obterm_valor_tributo(elem_pai, nomes_tags):
            if elem_pai is None:
                return 0.0
            for sub in elem_pai.iter():
                tag_nome = sub.tag.split('}')[-1]  # remove o namespace
                if tag_nome.lower() in [n.lower() for n in nomes_tags]:
                    if sub.text:
                        try:
                            return float(sub.text.replace(',', '.'))
                        except ValueError:
                            pass
            return 0.0

        valor_total = obterm_valor_tributo(valores_elem, ['ValorServicos', 'vServ'])
        valor_ir = obterm_valor_tributo(valores_elem, ['ValorIr', 'vIr', 'Ir'])
        valor_inss = obterm_valor_tributo(valores_elem, ['ValorInss', 'vInss', 'Inss'])
        valor_iss = obterm_valor_tributo(valores_elem, ['ValorIss', 'vIss', 'Iss'])

        # Busca flexível aceitando ValorPis/vPis, ValorCofins/vCofins, ValorCsll/vCsll
        v_pis = obterm_valor_tributo(valores_elem, ['ValorPis', 'vPis', 'Pis'])
        v_cofins = obterm_valor_tributo(valores_elem, ['ValorCofins', 'vCofins', 'Cofins'])
        v_csll = obterm_valor_tributo(valores_elem, ['ValorCsll', 'vCsll', 'Csll'])

        # TOTAIS
        soma_pis_cofins_csll = round(v_pis + v_cofins + v_csll, 2)
        total_impostos = round(valor_iss + valor_inss + v_pis + v_cofins + v_csll + valor_ir, 2)

        desc_elem = nfse.find('ns3:Servico/ns3:Discriminacao', namespaces)
        texto_discriminacao = desc_elem.text if desc_elem is not None else ''
        medico = extrair_nome_medico(texto_discriminacao)

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
            'SomaPisCofinsCsll': soma_pis_cofins_csll,
            'ValorPis': v_pis,
            'ValorCofins': v_cofins,
            'ValorCsll': v_csll,
            'Medico': medico,
        }

        notas_fiscais.append(nota)

    return notas_fiscais

def ler_todos_os_xmls():
    """Abre o seletor de arquivos e retorna uma lista unificada com os dicionários de todas as notas."""
    caminhos_arquivos = selecionar_arquivos_xml()
    
    if not caminhos_arquivos:
        return []

    todas_as_notas = []
    for caminho in caminhos_arquivos:
        notas = extrair_dados_xml(caminho)
        todas_as_notas.extend(notas)

    return todas_as_notas