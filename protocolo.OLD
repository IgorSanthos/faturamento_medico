import pandas as pd


def gerar_protocolo(
    total_faturamento,
    total_iss,
    total_inss,
    total_pis,
    total_cofins,
    total_csll,
    total_ir
):
    """
    Monta o protocolo de impostos enviados.
    """

    dados_protocolo = [

        [
            "Planilha de Faturamento 08/2026",
            "",
            total_faturamento
        ],

        [
            "Guia de ISS 08/2026",
            "10/09/2026",
            total_iss
        ],

        [
            "Darf GPS 08/2026",
            "18/09/2026",
            total_inss
        ],

        [
            "Boleto de Honorários 08/2026",
            "25/09/2026",
            1621.00
        ],

        [
            "Darf Pis 08/2026",
            "25/09/2026",
            total_pis
        ],

        [
            "Darf Cofins 08/2026",
            "25/09/2026",
            total_cofins
        ],

        [
            "Darf CSLL 08/2026",
            "30/09/2026",
            total_csll
        ],

        [
            "Darf IRPJ 08/2026",
            "30/09/2026",
            total_ir
        ]
    ]

    total_protocolo = sum(
        linha[2]
        for linha in dados_protocolo
    )

    dados_protocolo.append(
        [
            "TOTAL",
            "",
            total_protocolo
        ]
    )

    df_protocolo = pd.DataFrame(
        dados_protocolo,
        columns=[
            "",
            "Vencimento",
            "Valor R$"
        ]
    )

    return df_protocolo