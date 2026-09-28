
import pandas as pd


def calcular_totais(df):
    """
    Calcula os totais financeiros das notas fiscais.

    Notas canceladas (SituacaoNota = C) não entram nos totais.
    """

    # ========================================================
    # EXCLUIR NOTAS CANCELADAS DOS CÁLCULOS
    # ========================================================

    if "SituacaoNota" in df.columns:
        df = df[
            df["SituacaoNota"]
            .fillna("")
            .astype(str)
            .str.upper()
            .str.strip() != "C"
        ].copy()

    return {
        "total_faturamento": float(
            df["ValorTotal"].sum()
        ),

        "total_iss": float(
            df["ValorIss"].sum()
        ),

        "total_iss_pago": float(
            df["ValorIssPago"].sum()
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
    detalhes_medicos = []

    # ========================================================
    # EXCLUIR NOTAS CANCELADAS DOS CÁLCULOS
    # ========================================================

    if "SituacaoNota" in df.columns:
        df = df[
            df["SituacaoNota"]
            .fillna("")
            .astype(str)
            .str.upper()
            .str.strip()
            != "C"
        ].copy()

    # ========================================================
    # NORMALIZAR MÉDICO
    # ========================================================

    if "Medico" not in df.columns:
        df["Medico"] = ""

    df["Medico"] = df["Medico"].fillna("").astype(str).str.strip()

    # ========================================================
    # MÉDICOS
    # ========================================================

    medicos = list(df["Medico"].unique())

    medicos.sort(key=lambda x: (x == "", x))

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
        df_medico = df[df["Medico"] == medico]

        # ====================================================
        # FATURAMENTO
        # ====================================================

        faturamento = float(df_medico["ValorTotal"].sum())

        # ====================================================
        # ISS
        # ====================================================

        iss_destacado = float(
            df_medico["ValorIss"].sum()
        )

        iss_pago = float(
            df_medico["ValorIssPago"].fillna(0).sum()
        )

        iss_a_pagar = max(
            round(iss_destacado - iss_pago, 2),
            0
        )

        # ====================================================
        # INSS
        # ====================================================

        inss_destacado = float(df_medico["ValorInss"].sum())

        # ====================================================
        # IR RETIDO
        # ====================================================

        ir_destacado = float(df_medico["ValorIr"].sum())

        # ====================================================
        # PCC
        # SOMENTE NOTAS COM ValorPccRetido > 0
        # ====================================================

        df_pcc = df_medico[df_medico["ValorPccRetido"].fillna(0) > 0].copy()

        base_pcc = float(df_pcc["ValorTotal"].sum())

        pcc_retido = float(df_medico["ValorPccRetido"].fillna(0).sum())

        # ====================================================
        # COFINS
        # ====================================================

        cofins_calculado = round(faturamento * 0.03, 2)

        cofins_retido_pcc = round(base_pcc * 0.03, 2)

        cofins_a_pagar = max(round(cofins_calculado - cofins_retido_pcc, 2), 0)

        # ====================================================
        # PIS
        # ====================================================

        pis_calculado = round(faturamento * 0.0065, 2)

        pis_retido_pcc = round(base_pcc * 0.0065, 2)

        pis_a_pagar = max(round(pis_calculado - pis_retido_pcc, 2), 0)

        # ====================================================
        # CSLL
        # ====================================================

        csll_calculado = round(faturamento * 0.0108, 2)

        csll_retido_pcc = round(base_pcc * 0.01, 2)

        csll_a_pagar = max(round(csll_calculado - csll_retido_pcc, 2), 0)

        # ====================================================
        # IRPJ
        # ====================================================

        ir_calculado = round(faturamento * 0.012, 2)

        ir_a_pagar = max(round(ir_calculado - ir_destacado, 2), 0)

        # ====================================================
        # HONORÁRIO / DARF GPS
        # ====================================================

        honorario = float(honorario_por_medico)

        darf_gps = float(darf_gps_por_medico)

        # ====================================================
        # TOTAL DOS IMPOSTOS DO MÉDICO
        # ====================================================

        total_impostos = round(
            honorario
            + iss_a_pagar
            + iss_a_pagar
            + darf_gps
            + cofins_a_pagar
            + pis_a_pagar   
            + csll_a_pagar
            + ir_a_pagar,
            2,
        )

        # ====================================================
        # TOTAL LÍQUIDO
        # ====================================================

        total_liquido = round(
            df_medico.apply(
                lambda linha: float(linha.get("ValorTotal", 0) or 0)
                - float(linha.get("ValorIr", 0) or 0)
                - float(linha.get("ValorPccRetido", 0) or 0),
                axis=1,
            ).sum(),
            2,
        )

        # ====================================================
        # ACUMULAR TOTAIS A PAGAR
        # ====================================================

        total_pis_a_pagar += pis_a_pagar
        total_cofins_a_pagar += cofins_a_pagar
        total_csll_a_pagar += csll_a_pagar
        total_ir_a_pagar += ir_a_pagar

        # ====================================================
        # DEMONSTRATIVO
        # ====================================================

        linhas.append([medico, total_impostos])

        # ====================================================
        # DETALHAMENTO DO MÉDICO
        # ====================================================

        detalhes_medicos.append(
            {
                "medico": medico,
                "faturamento": round(faturamento, 2),
                "iss": round(iss_destacado, 2),
                "iss_pago": round(iss_pago, 2),
                "iss_a_pagar": round(iss_a_pagar, 2),
                "inss": round(inss_destacado, 2),
                "ir_destacado": round(ir_destacado, 2),
                "pcc_retido": round(pcc_retido, 2),
                "base_pcc": round(base_pcc, 2),
                "pis_calculado": pis_calculado,
                "pis_retido_pcc": pis_retido_pcc,
                "pis_a_pagar": pis_a_pagar,
                "cofins_calculado": cofins_calculado,
                "cofins_retido_pcc": cofins_retido_pcc,
                "cofins_a_pagar": cofins_a_pagar,
                "csll_calculado": csll_calculado,
                "csll_retido_pcc": csll_retido_pcc,
                "csll_a_pagar": csll_a_pagar,
                "ir_calculado": ir_calculado,
                "ir_a_pagar": ir_a_pagar,
                "honorario": round(honorario, 2),
                "darf_gps": round(darf_gps, 2),
                "total_liquido": total_liquido,
                "total_impostos": total_impostos,
            }
        )

    # ========================================================
    # DATAFRAME DO DEMONSTRATIVO
    # ========================================================

    demonstrativo = pd.DataFrame(linhas, columns=["Médico", "Valor dos Impostos"])

    # ========================================================
    # TOTAL GERAL DO DEMONSTRATIVO
    # ========================================================

    total_demonstrativo = demonstrativo["Valor dos Impostos"].sum()

    demonstrativo.loc[len(demonstrativo)] = ["TOTAL", round(total_demonstrativo, 2)]

    # ========================================================
    # TOTAIS A PAGAR
    # ========================================================

    totais_a_pagar = {
        "pis": round(total_pis_a_pagar, 2),
        "cofins": round(total_cofins_a_pagar, 2),
        "csll": round(total_csll_a_pagar, 2),
        "ir": round(total_ir_a_pagar, 2),
    }

    # ========================================================
    # RETORNO
    # ========================================================

    return demonstrativo, totais_a_pagar, detalhes_medicos
