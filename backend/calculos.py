import pandas as pd


def calcular_totais(df):
    """
    Calcula os totais financeiros das notas fiscais.
    """

    return {
        "total_faturamento": float(
            df["ValorTotal"].sum()
        ),

        "total_iss": float(
            df["ValorIss"].sum()
        ),

        "total_inss": float(
            df["ValorInss"].sum()
        ),

        "total_pis": float(
            df["ValorPisRetido"].sum()
        ),

        "total_cofins": float(
            df["ValorCofinsRetido"].sum()
        ),

        "total_csll": float(
            df["ValorCsllRetido"].sum()
        ),

        "total_ir": float(
            df["ValorIr"].sum()
        ),

        "total_impostos": float(
            df["TotalImpostos"].sum()
        ),
    }


def gerar_demonstrativo(
    dados_extraidos,
    honorario_por_medico=0,
    darf_gps_por_medico=0,
):
    df = pd.DataFrame(dados_extraidos)

    linhas = []

    # ========================================================
    # NORMALIZAR MÉDICO
    # ========================================================

    if "Medico" not in df.columns:
        df["Medico"] = ""

    df["Medico"] = (
        df["Medico"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    # ========================================================
    # MÉDICOS
    # ========================================================

    medicos = list(
        df["Medico"].unique()
    )

    medicos.sort(
        key=lambda x: (
            x == "",
            x
        )
    )

    # ========================================================
    # TOTAIS A PAGAR
    # ========================================================

    total_pis_a_pagar = 0.0
    total_cofins_a_pagar = 0.0
    total_csll_a_pagar = 0.0
    total_ir_a_pagar = 0.0

    # ========================================================
    # PROCESSAR CADA MÉDICO
    # ========================================================

    for medico in medicos:

        df_medico = df[
            df["Medico"] == medico
        ]

        # ====================================================
        # BASE
        # ====================================================

        base_calculo = df_medico[
            "ValorTotal"
        ].sum()

        # ====================================================
        # VALORES DESTACADOS / RETIDOS
        # ====================================================

        iss_destacado = (
            df_medico["ValorIss"].sum()
        )

        pis_retido = (
            df_medico["ValorPisRetido"].sum()
        )

        cofins_retido = (
            df_medico["ValorCofinsRetido"].sum()
        )

        csll_retida = (
            df_medico["ValorCsllRetido"].sum()
        )

        ir_destacado = (
            df_medico["ValorIr"].sum()
        )

        # ====================================================
        # COFINS
        # ====================================================

        cofins_calculado = round(
            base_calculo * 0.03,
            2
        )

        cofins_a_pagar = max(
            round(
                cofins_calculado
                - cofins_retido,
                2
            ),
            0
        )

        # ====================================================
        # PIS
        # ====================================================

        pis_calculado = round(
            base_calculo * 0.0065,
            2
        )

        pis_a_pagar = max(
            round(
                pis_calculado
                - pis_retido,
                2
            ),
            0
        )

        # ====================================================
        # CSLL
        # ====================================================

        csll_calculado = round(
            base_calculo * 0.0108,
            2
        )

        csll_a_pagar = max(
            round(
                csll_calculado
                - csll_retida,
                2
            ),
            0
        )

        # ====================================================
        # IRPJ
        # ====================================================

        ir_calculado = round(
            base_calculo * 0.012,
            2
        )

        ir_a_pagar = max(
            round(
                ir_calculado
                - ir_destacado,
                2
            ),
            0
        )

        # ====================================================
        # ACUMULAR TOTAIS A PAGAR
        # ====================================================

        total_pis_a_pagar += pis_a_pagar

        total_cofins_a_pagar += (
            cofins_a_pagar
        )

        total_csll_a_pagar += (
            csll_a_pagar
        )

        total_ir_a_pagar += (
            ir_a_pagar
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
            round(
                total,
                2
            )
        ])

    # ========================================================
    # DATAFRAME DO DEMONSTRATIVO
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
        demonstrativo[
            "Valor dos Impostos"
        ].sum()
    )

    demonstrativo.loc[
        len(demonstrativo)
    ] = [
        "TOTAL",
        round(
            total_demonstrativo,
            2
        )
    ]

    # ========================================================
    # TOTAIS A PAGAR
    # ========================================================

    totais_a_pagar = {
        "pis": round(
            total_pis_a_pagar,
            2
        ),

        "cofins": round(
            total_cofins_a_pagar,
            2
        ),

        "csll": round(
            total_csll_a_pagar,
            2
        ),

        "ir": round(
            total_ir_a_pagar,
            2
        )
    }

    return demonstrativo, totais_a_pagar