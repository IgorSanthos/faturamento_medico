import pandas as pd


def gerar_protocolo(
    dados_extraidos,
    total_faturamento=0,
    total_iss=0,
    total_inss=0,
    honorario_total=0,
):
    """
    Gera o protocolo de impostos.

    Notas canceladas (SituacaoNota = C) não entram
    nos cálculos do protocolo.

    Base de cálculo:
        Total do faturamento bruto das notas válidas.

    Fórmulas:
        PIS    = faturamento * 0,65% - PIS retido
        COFINS = faturamento * 3,00% - COFINS retido
        CSLL   = faturamento * 1,08% - CSLL retida
        IRPJ   = faturamento * 1,20% - IR retido

    Regra:
        Se o resultado de algum imposto for negativo,
        o protocolo apresenta R$ 0,00.
    """

    df = pd.DataFrame(dados_extraidos)

    # ========================================================
    # EXCLUIR NOTAS CANCELADAS
    # ========================================================

    if "SituacaoNota" in df.columns:
        df = df[
            df["SituacaoNota"]
            .fillna("")
            .astype(str)
            .str.upper()
            .str.strip() != "C"
        ].copy()

    # ========================================================
    # GARANTIR COLUNAS DOS IMPOSTOS
    # ========================================================

    colunas_impostos = [
        "ValorPisRetido",
        "ValorCofinsRetido",
        "ValorCsllRetido",
        "ValorIr",
    ]

    for coluna in colunas_impostos:
        if coluna not in df.columns:
            df[coluna] = 0

        df[coluna] = pd.to_numeric(
            df[coluna],
            errors="coerce"
        ).fillna(0)

    # ========================================================
    # BASE DE CÁLCULO
    # ========================================================

    base_calculo = float(
        total_faturamento or 0
    )

    # ========================================================
    # VALORES RETIDOS
    # ========================================================

    pis_retido = round(
        df["ValorPisRetido"].sum(),
        2
    )

    cofins_retido = round(
        df["ValorCofinsRetido"].sum(),
        2
    )

    csll_retida = round(
        df["ValorCsllRetido"].sum(),
        2
    )

    ir_retido = round(
        df["ValorIr"].sum(),
        2
    )

    # ========================================================
    # PIS
    # ========================================================

    pis_calculado = round(
        base_calculo * 0.0065,
        2
    )

    pis_a_pagar = max(
        round(
            pis_calculado - pis_retido,
            2
        ),
        0
    )

    # ========================================================
    # COFINS
    # ========================================================

    cofins_calculado = round(
        base_calculo * 0.03,
        2
    )

    cofins_a_pagar = max(
        round(
            cofins_calculado - cofins_retido,
            2
        ),
        0
    )

    # ========================================================
    # CSLL
    # ========================================================

    csll_calculado = round(
        base_calculo * 0.0108,
        2
    )

    csll_a_pagar = max(
        round(
            csll_calculado - csll_retida,
            2
        ),
        0
    )

    # ========================================================
    # IRPJ
    # ========================================================

    ir_calculado = round(
        base_calculo * 0.012,
        2
    )

    ir_a_pagar = max(
        round(
            ir_calculado - ir_retido,
            2
        ),
        0
    )

    # ========================================================
    # OUTROS VALORES
    # ========================================================

    honorario = round(
        float(honorario_total or 0),
        2
    )

    iss = round(
        float(total_iss or 0),
        2
    )

    darf_gps = round(
        float(total_inss or 0),
        2
    )

    # ========================================================
    # TOTAL
    # ========================================================

    total = round(
        honorario
        + iss
        + darf_gps
        + cofins_a_pagar
        + pis_a_pagar
        + csll_a_pagar
        + ir_a_pagar,
        2,
    )

    # ========================================================
    # PROTOCOLO
    # ========================================================

    linhas = [
        {
            "Descrição": "Honorário",
            "Vencimento": "25/09/2026",
            "Valor R$": honorario
        },

        {
            "Descrição": "ISS",
            "Vencimento": "10/09/2026",
            "Valor R$": iss
        },

        {
            "Descrição": "DARF / GPS",
            "Vencimento": "18/09/2026",
            "Valor R$": darf_gps
        },

        {
            "Descrição": "COFINS a pagar",
            "Vencimento": "25/09/2026",
            "Valor R$": cofins_a_pagar
        },

        {
            "Descrição": "PIS a pagar",
            "Vencimento": "25/09/2026",
            "Valor R$": pis_a_pagar
        },

        {
            "Descrição": "CSLL a pagar",
            "Vencimento": "30/09/2026",
            "Valor R$": csll_a_pagar
        },

        {
            "Descrição": "IRPJ a pagar",
            "Vencimento": "30/09/2026",
            "Valor R$": ir_a_pagar
        },

        {
            "Descrição": "TOTAL",
            "Vencimento": "",
            "Valor R$": total
        },
    ]

    return pd.DataFrame(linhas)

