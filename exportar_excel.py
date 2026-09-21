import openpyxl
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter


def gerar_planilha_notas(
    dados_notas,
    caminho_saida="relatorio_notas_fiscais.xlsx",
    honorario_por_medico=0,
    darf_gps_por_medico=0
):
    """
    Gera um arquivo Excel completo contendo:

    1. Planilha Geral
    2. Uma aba para cada médico

    Os cálculos das abas dos médicos seguem a mesma regra
    utilizada na página individual do médico no Streamlit.
    """

    wb = Workbook()

    # ========================================================
    # ESTILOS
    # ========================================================

    fonte_titulo = Font(
        bold=True,
        size=14
    )

    fonte_cabecalho = Font(
        bold=True
    )

    fonte_total = Font(
        bold=True
    )

    alinhamento_centro = Alignment(
        horizontal="center",
        vertical="center"
    )

    alinhamento_esquerda = Alignment(
        horizontal="left",
        vertical="center"
    )

    borda = Border(
        left=Side(style="thin"),
        right=Side(style="thin"),
        top=Side(style="thin"),
        bottom=Side(style="thin")
    )

    formato_moeda = 'R$ #,##0.00'

    # ========================================================
    # MÉDICOS ENCONTRADOS
    # ========================================================

    medicos = sorted(
        set(
            nota.get("Medico", "").strip()
            for nota in dados_notas
            if nota.get("Medico", "").strip()
        )
    )

    quantidade_medicos = len(medicos)

    # ========================================================
    # ABA GERAL
    # ========================================================

    ws = wb.active
    ws.title = "Planilha Geral"

    ws["A1"] = "PLANILHA DE FATURAMENTO"
    ws["A1"].font = fonte_titulo

    # ========================================================
    # CABEÇALHOS DAS NOTAS
    # ========================================================

    cabecalhos = [
        "DATA",
        "CLIENTE",
        "N.FISCAL",
        "VALOR",
        "IR",
        "INSS",
        "PIS/COFINS/CSLL",
        "VALOR LÍQUIDO",
        "MÉDICO"
    ]

    linha = 3

    for coluna, cabecalho in enumerate(
        cabecalhos,
        start=1
    ):

        celula = ws.cell(
            row=linha,
            column=coluna,
            value=cabecalho
        )

        celula.font = fonte_cabecalho
        celula.alignment = alinhamento_centro
        celula.border = borda

    linha += 1

    linha_inicio_notas = linha

    # ========================================================
    # NOTAS FISCAIS
    # ========================================================

    for nota in dados_notas:

        data = nota.get(
            "DataEmissao",
            ""
        )

        cliente = nota.get(
            "TomadorServico",
            ""
        )

        numero_nf = nota.get(
            "NumeroNF",
            ""
        )

        valor = float(
            nota.get("ValorTotal", 0)
        )

        ir = float(
            nota.get("ValorIr", 0)
        )

        inss = float(
            nota.get("ValorInss", 0)
        )

        pis_cofins_csll = float(
            nota.get("SomaPisCofinsCsll", 0)
        )

        medico = nota.get(
            "Medico",
            ""
        ).strip()

        ws.cell(
            row=linha,
            column=1,
            value=data
        )

        ws.cell(
            row=linha,
            column=2,
            value=cliente
        )

        ws.cell(
            row=linha,
            column=3,
            value=numero_nf
        )

        valores = [
            valor,
            ir,
            inss,
            pis_cofins_csll
        ]

        for coluna, valor_celula in enumerate(
            valores,
            start=4
        ):

            celula = ws.cell(
                row=linha,
                column=coluna,
                value=valor_celula
            )

            celula.number_format = formato_moeda

        # VALOR LÍQUIDO
        celula_liquido = ws.cell(
            row=linha,
            column=8,
            value=(
                f"=D{linha}-E{linha}"
                f"-F{linha}-G{linha}"
            )
        )

        celula_liquido.number_format = formato_moeda

        ws.cell(
            row=linha,
            column=9,
            value=medico
        )

        for coluna in range(1, 10):

            ws.cell(
                row=linha,
                column=coluna
            ).border = borda

        linha += 1

    linha_fim_notas = linha - 1

    # ========================================================
    # LARGURA DAS COLUNAS
    # ========================================================

    larguras = {
        "A": 14,
        "B": 40,
        "C": 14,
        "D": 16,
        "E": 14,
        "F": 14,
        "G": 20,
        "H": 18,
        "I": 30
    }

    for coluna, largura in larguras.items():

        ws.column_dimensions[coluna].width = largura

    # ========================================================
    # DEMONSTRATIVO
    # ========================================================

    linha += 2

    ws.cell(
        row=linha,
        column=1,
        value="DEMONSTRATIVO DE IMPOSTOS"
    ).font = fonte_titulo

    linha += 1

    ws.cell(
        row=linha,
        column=1,
        value="MÉDICO"
    ).font = fonte_cabecalho

    ws.cell(
        row=linha,
        column=2,
        value="VALOR DOS IMPOSTOS"
    ).font = fonte_cabecalho

    linha += 1

    linha_inicio_demonstrativo = linha

    # ========================================================
    # DEMONSTRATIVO POR MÉDICO
    # ========================================================

    totais_medicos = []

    for medico in medicos:

        notas_medico = [
            nota
            for nota in dados_notas
            if nota.get("Medico", "").strip()
            == medico
        ]

        # ----------------------------------------------------
        # BASE
        # ----------------------------------------------------

        base_calculo = sum(
            float(nota.get("ValorTotal", 0))
            for nota in notas_medico
        )

        # ----------------------------------------------------
        # DESTACADOS
        # ----------------------------------------------------

        iss_destacado = sum(
            float(nota.get("ValorIss", 0))
            for nota in notas_medico
        )

        pis_destacado = sum(
            float(nota.get("ValorPis", 0))
            for nota in notas_medico
        )

        cofins_destacado = sum(
            float(nota.get("ValorCofins", 0))
            for nota in notas_medico
        )

        csll_destacado = sum(
            float(nota.get("ValorCsll", 0))
            for nota in notas_medico
        )

        ir_destacado = sum(
            float(nota.get("ValorIr", 0))
            for nota in notas_medico
        )

        # ----------------------------------------------------
        # CÁLCULOS
        # ----------------------------------------------------

        cofins_calculado = round(
            base_calculo * 0.03,
            2
        )

        cofins_a_pagar = round(
            cofins_calculado - cofins_destacado,
            2
        )

        pis_calculado = round(
            base_calculo * 0.0065,
            2
        )

        pis_a_pagar = round(
            pis_calculado - pis_destacado,
            2
        )

        csll_calculado = round(
            base_calculo * 0.0108,
            2
        )

        csll_a_pagar = round(
            csll_calculado - csll_destacado,
            2
        )

        ir_calculado = round(
            base_calculo * 0.012,
            2
        )

        ir_a_pagar = round(
            ir_calculado - ir_destacado,
            2
        )

        # ----------------------------------------------------
        # TOTAL
        # ----------------------------------------------------

        total = round(
            honorario_por_medico
            + iss_destacado
            + darf_gps_por_medico
            + cofins_a_pagar
            + pis_a_pagar
            + csll_a_pagar
            + ir_a_pagar,
            2
        )

        totais_medicos.append(total)

        ws.cell(
            row=linha,
            column=1,
            value=medico
        )

        celula = ws.cell(
            row=linha,
            column=2,
            value=total
        )

        celula.number_format = formato_moeda

        linha += 1

    # ========================================================
    # TOTAL GERAL
    # ========================================================

    total_geral = round(
        sum(totais_medicos),
        2
    )

    ws.cell(
        row=linha,
        column=1,
        value="TOTAL"
    ).font = fonte_total

    celula = ws.cell(
        row=linha,
        column=2,
        value=total_geral
    )

    celula.font = fonte_total
    celula.number_format = formato_moeda

    # ========================================================
    # ABAS INDIVIDUAIS DOS MÉDICOS
    # ========================================================

    for medico in medicos:

        notas_medico = [
            nota
            for nota in dados_notas
            if nota.get("Medico", "").strip()
            == medico
        ]

        # ----------------------------------------------------
        # NOME DA ABA
        # ----------------------------------------------------

        nome_aba = medico

        caracteres_invalidos = [
            "\\",
            "/",
            "*",
            "[",
            "]",
            ":",
            "?"
        ]

        for caractere in caracteres_invalidos:
            nome_aba = nome_aba.replace(
                caractere,
                ""
            )

        nome_aba = nome_aba[:31]

        ws_medico = wb.create_sheet(
            title=nome_aba
        )

        # ----------------------------------------------------
        # TÍTULO
        # ----------------------------------------------------

        ws_medico["A1"] = medico
        ws_medico["A1"].font = fonte_titulo

        ws_medico["A2"] = "FATURAMENTO - AGOSTO - 2026"
        ws_medico["A2"].font = fonte_cabecalho

        # ----------------------------------------------------
        # CABEÇALHO FATURAMENTO
        # ----------------------------------------------------

        linha_medico = 4

        cabecalhos_medico = [
            "DATA",
            "CLIENTE",
            "N.FISCAL",
            "VALOR",
            "IR",
            "PIS-COFINS",
            "TAXA ADM",
            "VALOR LÍQ."
        ]

        for coluna, cabecalho in enumerate(
            cabecalhos_medico,
            start=1
        ):

            celula = ws_medico.cell(
                row=linha_medico,
                column=coluna,
                value=cabecalho
            )

            celula.font = fonte_cabecalho
            celula.alignment = alinhamento_centro
            celula.border = borda

        linha_medico += 1

        linha_inicio_faturamento = linha_medico

        # ----------------------------------------------------
        # NOTAS DO MÉDICO
        # ----------------------------------------------------

        for nota in notas_medico:

            valor = float(
                nota.get("ValorTotal", 0)
            )

            ir = float(
                nota.get("ValorIr", 0)
            )

            pis = float(
                nota.get("ValorPis", 0)
            )

            cofins = float(
                nota.get("ValorCofins", 0)
            )

            csll = float(
                nota.get("ValorCsll", 0)
            )

            pis_cofins = (
                pis
                + cofins
                + csll
            )

            taxa_adm = 0.00

            valor_liquido = (
                valor
                - ir
                - pis_cofins
                - taxa_adm
            )

            valores = [
                nota.get("DataEmissao", ""),
                nota.get("TomadorServico", ""),
                nota.get("NumeroNF", ""),
                valor,
                ir,
                pis_cofins,
                taxa_adm,
                valor_liquido
            ]

            for coluna, valor_celula in enumerate(
                valores,
                start=1
            ):

                celula = ws_medico.cell(
                    row=linha_medico,
                    column=coluna,
                    value=valor_celula
                )

                celula.border = borda

                if coluna >= 4:

                    celula.number_format = formato_moeda

            linha_medico += 1

        linha_fim_faturamento = (
            linha_medico - 1
        )

        # ----------------------------------------------------
        # TOTAIS FATURAMENTO
        # ----------------------------------------------------

        total_valor = sum(
            float(nota.get("ValorTotal", 0))
            for nota in notas_medico
        )

        total_ir = sum(
            float(nota.get("ValorIr", 0))
            for nota in notas_medico
        )

        total_pis_cofins = sum(
            float(nota.get("ValorPis", 0))
            + float(nota.get("ValorCofins", 0))
            + float(nota.get("ValorCsll", 0))
            for nota in notas_medico
        )

        total_taxa_adm = 0.00

        total_liquido = (
            total_valor
            - total_ir
            - total_pis_cofins
            - total_taxa_adm
        )

        valores_totais = [
            "",
            "TOTAL",
            "",
            total_valor,
            total_ir,
            total_pis_cofins,
            total_taxa_adm,
            total_liquido
        ]

        for coluna, valor_celula in enumerate(
            valores_totais,
            start=1
        ):

            celula = ws_medico.cell(
                row=linha_medico,
                column=coluna,
                value=valor_celula
            )

            celula.font = fonte_total
            celula.border = borda

            if coluna >= 4:

                celula.number_format = formato_moeda

        # ----------------------------------------------------
        # RESUMO
        # ----------------------------------------------------

        linha_medico += 3

        ws_medico.cell(
            row=linha_medico,
            column=1,
            value="RESUMO DO FATURAMENTO"
        ).font = fonte_titulo

        linha_medico += 1

        resumo = [
            ("Faturamento", total_valor),
            ("IR Destacado", total_ir),
            (
                "PIS / COFINS / CSLL Destacado",
                total_pis_cofins
            ),
            ("Valor Líquido", total_liquido)
        ]

        for nome, valor in resumo:

            ws_medico.cell(
                row=linha_medico,
                column=1,
                value=nome
            )

            celula = ws_medico.cell(
                row=linha_medico,
                column=2,
                value=valor
            )

            celula.number_format = formato_moeda

            linha_medico += 1

        # ----------------------------------------------------
        # IMPOSTOS
        # ----------------------------------------------------

        linha_medico += 2

        ws_medico.cell(
            row=linha_medico,
            column=1,
            value="IMPOSTOS"
        ).font = fonte_titulo

        linha_medico += 1

        # ----------------------------------------------------
        # VALORES DESTACADOS
        # ----------------------------------------------------

        total_iss_destacado = sum(
            float(nota.get("ValorIss", 0))
            for nota in notas_medico
        )

        total_pis_destacado = sum(
            float(nota.get("ValorPis", 0))
            for nota in notas_medico
        )

        total_cofins_destacado = sum(
            float(nota.get("ValorCofins", 0))
            for nota in notas_medico
        )

        total_csll_destacado = sum(
            float(nota.get("ValorCsll", 0))
            for nota in notas_medico
        )

        total_ir_destacado = sum(
            float(nota.get("ValorIr", 0))
            for nota in notas_medico
        )

        # ----------------------------------------------------
        # CÁLCULOS
        # ----------------------------------------------------

        base_calculo = total_valor

        cofins_calculado = round(
            base_calculo * 0.03,
            2
        )

        cofins_a_pagar = round(
            cofins_calculado
            - total_cofins_destacado,
            2
        )

        pis_calculado = round(
            base_calculo * 0.0065,
            2
        )

        pis_a_pagar = round(
            pis_calculado
            - total_pis_destacado,
            2
        )

        csll_calculado = round(
            base_calculo * 0.0108,
            2
        )

        csll_a_pagar = round(
            csll_calculado
            - total_csll_destacado,
            2
        )

        ir_calculado = round(
            base_calculo * 0.012,
            2
        )

        ir_a_pagar = round(
            ir_calculado
            - total_ir_destacado,
            2
        )

        # ----------------------------------------------------
        # NÚMEROS DAS NOTAS
        # ----------------------------------------------------

        numero_inicial = (
            notas_medico[0].get("NumeroNF", "")
            if notas_medico
            else ""
        )

        numero_final = (
            notas_medico[-1].get("NumeroNF", "")
            if notas_medico
            else ""
        )

        base_formatada = (
            f"{base_calculo:,.2f}"
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )

        # ----------------------------------------------------
        # TABELA DE IMPOSTOS
        # ----------------------------------------------------

        cabecalhos_impostos = [
            "COD.REC.",
            "IMPOSTOS",
            "VENCTO",
            "VALOR IMPOSTO",
            "DEDUÇÃO NF",
            "TOTAL"
        ]

        for coluna, cabecalho in enumerate(
            cabecalhos_impostos,
            start=1
        ):

            celula = ws_medico.cell(
                row=linha_medico,
                column=coluna,
                value=cabecalho
            )

            celula.font = fonte_cabecalho
            celula.alignment = alinhamento_centro
            celula.border = borda

        linha_medico += 1

        dados_impostos = [

            [
                "",
                "HONORÁRIO - 08/2026",
                "25/09/2026",
                0,
                0,
                honorario_por_medico
            ],

            [
                "04030",
                (
                    "ISS - SP - 2% - "
                    f"NF.{numero_inicial} A {numero_final} - "
                    f"Base de Calc R$ {base_formatada}"
                ),
                "10/09/2026",
                total_iss_destacado,
                0,
                total_iss_destacado
            ],

            [
                "",
                "DARF GPS - 08/2026",
                "18/09/2026",
                0,
                0,
                darf_gps_por_medico
            ],

            [
                "2172",
                (
                    "COFINS - 3% - "
                    f"Base de Cálculo R$ {base_formatada}"
                ),
                "25/09/2026",
                cofins_calculado,
                total_cofins_destacado,
                cofins_a_pagar
            ],

            [
                "8109",
                (
                    "PIS - 0,65% - "
                    f"Base de Cálculo R$ {base_formatada}"
                ),
                "25/09/2026",
                pis_calculado,
                total_pis_destacado,
                pis_a_pagar
            ],

            [
                "2372",
                (
                    "CONTRIBUIÇÃO SOCIAL - "
                    "Alíq.Reduzida - 1,08% - "
                    f"Base de Cálculo R$ {base_formatada}"
                ),
                "30/09/2026",
                csll_calculado,
                total_csll_destacado,
                csll_a_pagar
            ],

            [
                "2089",
                (
                    "I.R.P.J. - "
                    "Alíq.Reduzida - 1,2% - "
                    f"Base de Cálculo R$ {base_formatada}"
                ),
                "30/09/2026",
                ir_calculado,
                total_ir_destacado,
                ir_a_pagar
            ]
        ]

        for dados in dados_impostos:

            for coluna, valor_celula in enumerate(
                dados,
                start=1
            ):

                celula = ws_medico.cell(
                    row=linha_medico,
                    column=coluna,
                    value=valor_celula
                )

                celula.border = borda

                if coluna >= 4:

                    celula.number_format = formato_moeda

            linha_medico += 1

        # ----------------------------------------------------
        # TOTAL DOS IMPOSTOS
        # ----------------------------------------------------

        total_impostos_medico = round(
            honorario_por_medico
            + total_iss_destacado
            + darf_gps_por_medico
            + cofins_a_pagar
            + pis_a_pagar
            + csll_a_pagar
            + ir_a_pagar,
            2
        )

        ws_medico.cell(
            row=linha_medico,
            column=1,
            value="TOTAL"
        ).font = fonte_total

        celula = ws_medico.cell(
            row=linha_medico,
            column=6,
            value=total_impostos_medico
        )

        celula.font = fonte_total
        celula.number_format = formato_moeda

        # ----------------------------------------------------
        # LARGURA DAS COLUNAS
        # ----------------------------------------------------

        larguras_medico = {
            "A": 14,
            "B": 45,
            "C": 15,
            "D": 18,
            "E": 18,
            "F": 18,
            "G": 18,
            "H": 18
        }

        for coluna, largura in larguras_medico.items():

            ws_medico.column_dimensions[
                coluna
            ].width = largura

    # ========================================================
    # SALVA
    # ========================================================

    wb.save(caminho_saida)

    return caminho_saida