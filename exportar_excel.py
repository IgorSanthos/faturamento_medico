import openpyxl
from openpyxl.styles import Font, Alignment

def gerar_planilha_notas(dados_notas, caminho_saida="relatorio_notas_fiscais.xlsx"):
    """
    Cria a planilha completa com dados das notas, demonstrativo de médicos 
    e protocolo inteligente de impostos.
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Planilha Geral"

    # ========================================================
    # CABEÇALHOS DAS NOTAS FISCAIS
    # ========================================================
    cabecalhos = [
        "DATA", "CLIENTE", "N.FISCAL", "VALOR", 
        "IR", "INSS", "PIS/COFINS/CSLL", "VALOR LÍQUIDO", "MÉDICO"
    ]

    for col_num, cabecalho in enumerate(cabecalhos, 1):
        celula = ws.cell(row=1, column=col_num, value=cabecalho)
        celula.font = Font(bold=True)
        celula.alignment = Alignment(horizontal="center")

    # ========================================================
    # PREENCHIMENTO DAS NOTAS E EXTRAÇÃO DE MÉDICOS
    # ========================================================
    linha = 2
    medicos_encontrados = set()

    for nota in dados_notas:
        ws.cell(row=linha, column=1, value=nota.get("DataEmissao", ""))
        ws.cell(row=linha, column=2, value=nota.get("TomadorServico", ""))
        ws.cell(row=linha, column=3, value=nota.get("NumeroNF", ""))
        
        valor = float(nota.get("ValorTotal", 0))
        ir = float(nota.get("ValorIr", 0))
        inss = float(nota.get("ValorInss", 0))
        pis_cofins_csll = float(nota.get("SomaPisCofinsCsll", 0))
        
        # Atribuição de valores com formatação de moeda
        for col_idx, val in enumerate([valor, ir, inss, pis_cofins_csll], start=4):
            c = ws.cell(row=linha, column=col_idx, value=val)
            c.number_format = 'R$ #,##0.00'
        
        # Fórmula do Valor Líquido
        cel_liq = ws.cell(row=linha, column=8, value=f"=D{linha}-E{linha}-F{linha}-G{linha}")
        cel_liq.number_format = 'R$ #,##0.00'
        
        nome_medico = nota.get("Medico", "").strip()
        ws.cell(row=linha, column=9, value=nome_medico)
        
        if nome_medico:
            medicos_encontrados.add(nome_medico)
            
        linha += 1

    linha_fim_notas = linha - 1  

    # Ajuste dinâmico do tamanho das colunas principais
    ws.column_dimensions['A'].width = 12
    ws.column_dimensions['B'].width = 40
    ws.column_dimensions['C'].width = 12
    ws.column_dimensions['D'].width = 15
    ws.column_dimensions['E'].width = 12
    ws.column_dimensions['F'].width = 12
    ws.column_dimensions['G'].width = 18
    ws.column_dimensions['H'].width = 18
    ws.column_dimensions['I'].width = 30

    linha += 2  

    # ========================================================
    # BLOCO 1: DEMONSTRATIVO DE MÉDICOS
    # ========================================================
    ws.cell(row=linha, column=1, value="DEMONSTRATIVO").font = Font(bold=True)
    ws.cell(row=linha, column=2, value="IMPOSTOS").font = Font(bold=True)
    linha += 1
    
    linha_inicio_demonstrativo = linha
    
    if not medicos_encontrados:
        medicos_encontrados = ["DRA ALESSANDRA", "DR.ARIEL", "DRA HERICA"]
        
    for medico in sorted(medicos_encontrados):
        ws.cell(row=linha, column=1, value=medico)
        c_val = ws.cell(row=linha, column=2, value=0.00)
        c_val.number_format = 'R$ #,##0.00'
        linha += 1
        
    ws.cell(row=linha, column=1, value="TOTAL").font = Font(bold=True)
    c_tot = ws.cell(row=linha, column=2, value=f"=SUM(B{linha_inicio_demonstrativo}:B{linha-1})")
    c_tot.font = Font(bold=True)
    c_tot.number_format = 'R$ #,##0.00'

    linha += 3 

    # ========================================================
    # BLOCO 2: PROTOCOLO DE IMPOSTOS COM FÓRMULAS EXCEL
    # ========================================================
    ws.cell(row=linha, column=1, value="PROTOCOLO DE IMPOSTOS ENVIADOS").font = Font(bold=True)
    ws.cell(row=linha, column=2, value="Vencimento").font = Font(bold=True)
    ws.cell(row=linha, column=3, value="Valor R$").font = Font(bold=True)
    linha += 1
    
    ws.cell(row=linha, column=1, value="Planilha de Faturamento")
    linha += 1
    
    f_iss = f"=ROUND(SUM(D2:D{linha_fim_notas}) * 0.02, 2)"
    f_pis = f"=ROUND(MAX(0, (SUM(D2:D{linha_fim_notas}) * 0.0065) - (SUM(G2:G{linha_fim_notas}) * (0.65/4.65))), 2)"
    f_cofins = f"=ROUND(MAX(0, (SUM(D2:D{linha_fim_notas}) * 0.03) - (SUM(G2:G{linha_fim_notas}) * (3/4.65))), 2)"
    f_csll = f"=ROUND(MAX(0, (SUM(D2:D{linha_fim_notas}) * 0.0108) - (SUM(G2:G{linha_fim_notas}) * (1/4.65))), 2)"
    f_irpj = f"=ROUND(MAX(0, (SUM(D2:D{linha_fim_notas}) * 0.012) - SUM(E2:E{linha_fim_notas})), 2)"

    impostos = [
        ("Guia de ISS", "10/09", f_iss),
        ("Darf GPS", "18/09", 1507.53),
        ("Boleto de Honorários", "25/09", 1621.00),
        ("Darf Pis", "25/09", f_pis),
        ("Darf Cofins", "25/09", f_cofins),
        ("Darf CSLL", "30/09", f_csll),
        ("Darf IRPJ", "30/09", f_irpj)
    ]
    
    linha_inicio_impostos = linha
    for nome_imp, vencimento, formula_imp in impostos:
        ws.cell(row=linha, column=1, value=nome_imp)
        ws.cell(row=linha, column=2, value=vencimento)
        c_imp = ws.cell(row=linha, column=3, value=formula_imp)
        if isinstance(formula_imp, (int, float)):
            c_imp.number_format = 'R$ #,##0.00'
        linha += 1
        
    ws.cell(row=linha, column=1, value="TOTAL").font = Font(bold=True)
    c_tot_imp = ws.cell(row=linha, column=3, value=f"=SUM(C{linha_inicio_impostos}:C{linha-1})")
    c_tot_imp.font = Font(bold=True)
    c_tot_imp.number_format = 'R$ #,##0.00'
    
    linha += 2
    ws.cell(row=linha, column=1, value="Data do envio do Faturamento e Impostos:").font = Font(bold=True)

    # Salva o arquivo final
    wb.save(caminho_saida)
    return caminho_saida