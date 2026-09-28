
import pandas as pd


def gerar_protocolo(detalhes_medicos):
    """
    Gera o protocolo somando os valores já calculados
    individualmente para cada médico.

    O protocolo NÃO recalcula os impostos sobre o
    faturamento geral.

    Fonte dos valores:
        detalhes_medicos -> calculos.py
    """

    # ========================================================
    # GARANTIR LISTA
    # ========================================================

    if not detalhes_medicos:
        return pd.DataFrame(
            [
                {
                    "Descrição": "TOTAL",
                    "Vencimento": "",
                    "Calculado": "",
                    "Retido": "",
                    "A pagar": 0,
                }
            ]
        )

    # ========================================================
    # SOMAR VALORES DOS MÉDICOS
    # ========================================================

    honorario = round(
        sum(
            float(medico.get("honorario", 0) or 0)
            for medico in detalhes_medicos
        ),
        2,
    )

    iss_calculado = round(
        sum(
            float(medico.get("iss", 0) or 0)
            for medico in detalhes_medicos
        ),
        2,
    )

    iss_retido = round(
        sum(
            float(medico.get("iss_pago", 0) or 0)
            for medico in detalhes_medicos
        ),
        2,
    )

    iss_a_pagar = round(
        sum(
            float(medico.get("iss_a_pagar", 0) or 0)
            for medico in detalhes_medicos
        ),
        2,
    )

    darf_gps = round(
        sum(
            float(medico.get("darf_gps", 0) or 0)
            for medico in detalhes_medicos
        ),
        2,
    )

    pis_calculado = round(
        sum(
            float(medico.get("pis_calculado", 0) or 0)
            for medico in detalhes_medicos
        ),
        2,
    )

    pis_retido = round(
        sum(
            float(medico.get("pis_retido_pcc", 0) or 0)
            for medico in detalhes_medicos
        ),
        2,
    )

    pis_a_pagar = round(
        sum(
            float(medico.get("pis_a_pagar", 0) or 0)
            for medico in detalhes_medicos
        ),
        2,
    )

    cofins_calculado = round(
        sum(
            float(medico.get("cofins_calculado", 0) or 0)
            for medico in detalhes_medicos
        ),
        2,
    )

    cofins_retido = round(
        sum(
            float(medico.get("cofins_retido_pcc", 0) or 0)
            for medico in detalhes_medicos
        ),
        2,
    )

    cofins_a_pagar = round(
        sum(
            float(medico.get("cofins_a_pagar", 0) or 0)
            for medico in detalhes_medicos
        ),
        2,
    )

    csll_calculado = round(
        sum(
            float(medico.get("csll_calculado", 0) or 0)
            for medico in detalhes_medicos
        ),
        2,
    )

    csll_retida = round(
        sum(
            float(medico.get("csll_retido_pcc", 0) or 0)
            for medico in detalhes_medicos
        ),
        2,
    )

    csll_a_pagar = round(
        sum(
            float(medico.get("csll_a_pagar", 0) or 0)
            for medico in detalhes_medicos
        ),
        2,
    )

    faturamento_total = round(
        sum(
            float(medico.get("faturamento", 0) or 0)
            for medico in detalhes_medicos
        ),
        2,
    )

    ir_calculado = round(
        faturamento_total * 0.012,
        2,
    )

    ir_retido = round(
        sum(
            float(medico.get("ir_destacado", 0) or 0)
            for medico in detalhes_medicos
        ),
        2,
    )

    ir_a_pagar = max(
        round(
            ir_calculado - ir_retido,
            2
        ),
        0,
    )

    # ========================================================
    # TOTAL GERAL
    # ========================================================

    total = round(
        honorario
        + iss_a_pagar
        + darf_gps
        + cofins_a_pagar
        + pis_a_pagar
        + csll_a_pagar
        + ir_a_pagar,
        2,
    )

    # ========================================================
    # MONTAR PROTOCOLO
    # ========================================================

    linhas = [
        {
            "Descrição": "Honorário",
            "Vencimento": "25/09/2026",
            "Calculado": honorario,
            "Retido": 0,
            "A pagar": honorario,
        },
        {
            "Descrição": "ISS",
            "Vencimento": "10/09/2026",
            "Calculado": iss_calculado,
            "Retido": iss_retido,
            "A pagar": iss_a_pagar,
        },
        {
            "Descrição": "DARF / GPS",
            "Vencimento": "18/09/2026",
            "Calculado": darf_gps,
            "Retido": 0,
            "A pagar": darf_gps,
        },
        {
            "Descrição": "COFINS a pagar",
            "Vencimento": "25/09/2026",
            "Calculado": cofins_calculado,
            "Retido": cofins_retido,
            "A pagar": cofins_a_pagar,
        },
        {
            "Descrição": "PIS a pagar",
            "Vencimento": "25/09/2026",
            "Calculado": pis_calculado,
            "Retido": pis_retido,
            "A pagar": pis_a_pagar,
        },
        {
            "Descrição": "CSLL a pagar",
            "Vencimento": "30/09/2026",
            "Calculado": csll_calculado,
            "Retido": csll_retida,
            "A pagar": csll_a_pagar,
        },
        {
            "Descrição": "IRPJ a pagar",
            "Vencimento": "30/09/2026",
            "Calculado": ir_calculado,
            "Retido": ir_retido,
            "A pagar": ir_a_pagar,
        },
        {
            "Descrição": "TOTAL",
            "Vencimento": "",
            "Calculado": "",
            "Retido": "",
            "A pagar": total,
        },
    ]

    return pd.DataFrame(linhas)
