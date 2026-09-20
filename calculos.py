import pandas as pd


def calcular_totais(df):
    """
    Calcula os totais financeiros das notas fiscais.
    """

    return {
        "total_faturamento": df["ValorTotal"].sum(),
        "total_iss": df["ValorIss"].sum(),
        "total_inss": df["ValorInss"].sum(),
        "total_pis": df["ValorPis"].sum(),
        "total_cofins": df["ValorCofins"].sum(),
        "total_csll": df["ValorCsll"].sum(),
        "total_ir": df["ValorIr"].sum(),
        "total_impostos": df["TotalImpostos"].sum(),
    }


def gerar_demonstrativo(
    dados_extraidos,
    honorario_por_medico=0,
    darf_gps_por_medico=0
):
    df = pd.DataFrame(dados_extraidos)

    linhas = []

    medicos = sorted(
        df["Medico"].dropna().unique()
    )

    for medico in medicos:

        if not medico:
            continue

        df_medico = df[
            df["Medico"] == medico
        ]

        # ====================================================
        # BASE DE CÁLCULO
        # ====================================================

        base_calculo = df_medico["ValorTotal"].sum()

        # ====================================================
        # VALORES DESTACADOS NAS NOTAS
        # ====================================================

        iss_destacado = df_medico["ValorIss"].sum()
        pis_destacado = df_medico["ValorPis"].sum()
        cofins_destacado = df_medico["ValorCofins"].sum()
        csll_destacado = df_medico["ValorCsll"].sum()
        ir_destacado = df_medico["ValorIr"].sum()

        # ====================================================
        # COFINS
        # ====================================================

        cofins_calculado = round(
            base_calculo * 0.03,
            2
        )

        cofins_a_pagar = round(
            cofins_calculado - cofins_destacado,
            2
        )

        # ====================================================
        # PIS
        # ====================================================

        pis_calculado = round(
            base_calculo * 0.0065,
            2
        )

        pis_a_pagar = round(
            pis_calculado - pis_destacado,
            2
        )

        # ====================================================
        # CSLL
        # ====================================================

        csll_calculado = round(
            base_calculo * 0.0108,
            2
        )

        csll_a_pagar = round(
            csll_calculado - csll_destacado,
            2
        )

        # ====================================================
        # IRPJ
        # ====================================================

        ir_calculado = round(
            base_calculo * 0.012,
            2
        )

        ir_a_pagar = round(
            ir_calculado - ir_destacado,
            2
        )

        # ====================================================
        # TOTAL DO MÉDICO
        # ====================================================

        total = (
            honorario_por_medico
            + iss_destacado
            + darf_gps_por_medico
            + cofins_a_pagar
            + pis_a_pagar
            + csll_a_pagar
            + ir_a_pagar
        )

        linhas.append([
            medico,
            round(total, 2)
        ])

    # ========================================================
    # DATAFRAME
    # ========================================================

    demonstrativo = pd.DataFrame(
        linhas,
        columns=[
            "Médico",
            "Valor dos Impostos"
        ]
    )

    # ========================================================
    # TOTAL GERAL
    # ========================================================

    total_demonstrativo = (
        demonstrativo["Valor dos Impostos"].sum()
    )

    demonstrativo.loc[len(demonstrativo)] = [
        "TOTAL",
        round(total_demonstrativo, 2)
    ]

    return demonstrativo