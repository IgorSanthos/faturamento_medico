import pandas as pd
import streamlit as st
from formatacao import formatar_reais

def mostrar_pagina_medico(
    dados_extraidos,
    medico,
    honorario_por_medico=0,
    darf_gps_por_medico=0
    ):
    """Mostra a página individual de um médico."""

    # ========================================================
    # FILTRA AS NOTAS DO MÉDICO
    # ========================================================

    notas_medico = [
        nota
        for nota in dados_extraidos
        if nota.get("Medico", "") == medico
    ]

    if not notas_medico:
        st.warning("Nenhuma nota encontrada para este médico.")
        return

    # ========================================================
    # BOTÃO VOLTAR
    # ========================================================

    if st.button("⬅️ Voltar para o Demonstrativo"):

        st.session_state["pagina"] = "principal"
        st.session_state["medico_selecionado"] = None

        if "tabela_demonstrativo" in st.session_state:
            del st.session_state["tabela_demonstrativo"]

        st.rerun()

    st.divider()

    # ========================================================
    # TÍTULO
    # ========================================================

    st.title(f"{medico} - Planilha")

    st.subheader("FATURAMENTO - AGOSTO - 2026")

    # ========================================================
    # TABELA DE FATURAMENTO
    # ========================================================

    dados_faturamento = []

    for nota in notas_medico:

        valor = nota.get("ValorTotal", 0)
        ir = nota.get("ValorIr", 0)
        pis = nota.get("ValorPis", 0)
        cofins = nota.get("ValorCofins", 0)
        csll = nota.get("ValorCsll", 0)

        pis_cofins = pis + cofins + csll

        taxa_adm = 0.00

        valor_liquido = (
            valor
            - ir
            - pis_cofins
            - taxa_adm
        )

        dados_faturamento.append({
            "DATA": nota.get("DataEmissao", ""),
            "CLIENTE": nota.get("TomadorServico", ""),
            "N.FISCAL": nota.get("NumeroNF", ""),
            "VALOR": valor,
            "IR": ir,
            "PIS-COFINS": pis_cofins,
            "TAXA ADM": taxa_adm,
            "VALOR LÍQ.": valor_liquido,
        })

    # ========================================================
    # DATAFRAME
    # ========================================================

    df_faturamento = pd.DataFrame(
        dados_faturamento
    )

    # ========================================================
    # TOTAIS
    # ========================================================

    total_valor = df_faturamento["VALOR"].sum()

    total_ir_destacado = (
        df_faturamento["IR"].sum()
    )

    total_pis_cofins = (
        df_faturamento["PIS-COFINS"].sum()
    )

    total_taxa_adm = (
        df_faturamento["TAXA ADM"].sum()
    )

    total_liquido = (
        df_faturamento["VALOR LÍQ."].sum()
    )

    # ========================================================
    # LINHA TOTAL
    # ========================================================

    df_faturamento.loc[
        len(df_faturamento)
    ] = [
        "",
        "TOTAL",
        "",
        total_valor,
        total_ir_destacado,
        total_pis_cofins,
        total_taxa_adm,
        total_liquido,
    ]

    # ========================================================
    # FORMATA VALORES EM R$
    # ========================================================

    colunas_monetarias = [
        "VALOR",
        "IR",
        "PIS-COFINS",
        "TAXA ADM",
        "VALOR LÍQ."
    ]

    for coluna in colunas_monetarias:

        df_faturamento[coluna] = (
            df_faturamento[coluna]
            .apply(formatar_reais)
        )

    # ========================================================
    # MOSTRA TABELA
    # ========================================================

    st.dataframe(
        df_faturamento,
        width="stretch",
        hide_index=True
    )

    # ========================================================
    # RESUMO
    # ========================================================

    st.divider()

    st.subheader("📊 RESUMO DO FATURAMENTO")

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Faturamento",
            formatar_reais(total_valor)
        )

    with col2:

        st.metric(
            "IR Destacado",
            formatar_reais(total_ir_destacado)
        )

    with col3:

        st.metric(
            "PIS / COFINS / CSLL Destacado",
            formatar_reais(total_pis_cofins)
        )

    with col4:

        st.metric(
            "Valor Líquido",
            formatar_reais(total_liquido)
        )

    # ========================================================
    # IMPOSTOS
    # ========================================================

    st.divider()

    st.subheader("IMPOSTOS")

    # ========================================================
    # VALORES DESTACADOS NOS XMLs
    # ========================================================

    total_iss_destacado = sum(
        nota.get("ValorIss", 0)
        for nota in notas_medico
    )

    total_pis_destacado = sum(
        nota.get("ValorPis", 0)
        for nota in notas_medico
    )

    total_cofins_destacado = sum(
        nota.get("ValorCofins", 0)
        for nota in notas_medico
    )

    total_csll_destacado = sum(
        nota.get("ValorCsll", 0)
        for nota in notas_medico
    )

    total_ir_destacado = sum(
        nota.get("ValorIr", 0)
        for nota in notas_medico
    )

    # ========================================================
    # BASE DE CÁLCULO
    # ========================================================

    base_calculo = total_valor

    base_formatada = (
        formatar_reais(base_calculo)
        .replace("R$ ", "")
    )

    # ========================================================
    # CÁLCULO DO PIS
    # ========================================================

    pis_calculado = round(
        base_calculo * 0.0065,
        2
    )

    pis_a_pagar = round(
        pis_calculado - total_pis_destacado,
        2
    )

    # ========================================================
    # CÁLCULO DA COFINS
    # ========================================================

    cofins_calculado = round(
        base_calculo * 0.03,
        2
    )

    cofins_a_pagar = round(
        cofins_calculado - total_cofins_destacado,
        2
    )

    # ========================================================
    # CÁLCULO DA CSLL
    # ========================================================

    csll_calculado = round(
        base_calculo * 0.0108,
        2
    )

    csll_a_pagar = round(
        csll_calculado - total_csll_destacado,
        2
    )

    # ========================================================
    # CÁLCULO DO IR
    # ========================================================

    ir_calculado = round(
        base_calculo * 0.012,
        2
    )

    ir_a_pagar = round(
        ir_calculado - total_ir_destacado,
        2
    )

    # ========================================================
    # NÚMEROS DAS NOTAS
    # ========================================================

    numero_inicial = notas_medico[0].get(
        "NumeroNF",
        ""
    )

    numero_final = notas_medico[-1].get(
        "NumeroNF",
        ""
    )

    # ========================================================
    # TABELA DE IMPOSTOS
    # ========================================================

    dados_impostos = [

        # ----------------------------------------------------
        # HONORÁRIO
        # ----------------------------------------------------

        [
            "",
            "HONORÁRIO - 08/2026",
            "25/09/2026",
            0,
            0,
            honorario_por_medico,
        ],

        # ----------------------------------------------------
        # ISS
        # ----------------------------------------------------

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
            total_iss_destacado,
        ],

        # ----------------------------------------------------
        # DARF GPS
        # ----------------------------------------------------

        [
            "",
            "DARF GPS - 08/2026",
            "18/09/2026",
            0,
            0,
            darf_gps_por_medico,
        ],

        # ----------------------------------------------------
        # COFINS
        # ----------------------------------------------------

        [
            "2172",
            (
                "COFINS - 3% - "
                f"Base de Cálculo R$ {base_formatada}"
            ),
            "25/09/2026",
            cofins_calculado,
            total_cofins_destacado,
            cofins_a_pagar,
        ],

        # ----------------------------------------------------
        # PIS
        # ----------------------------------------------------

        [
            "8109",
            (
                "PIS - 0,65% - "
                f"Base de Cálculo R$ {base_formatada}"
            ),
            "25/09/2026",
            pis_calculado,
            total_pis_destacado,
            pis_a_pagar,
        ],

        # ----------------------------------------------------
        # CSLL
        # ----------------------------------------------------

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
            csll_a_pagar,
        ],

        # ----------------------------------------------------
        # IRPJ
        # ----------------------------------------------------

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
            ir_a_pagar,
        ],
    ]

    # ========================================================
    # DATAFRAME DOS IMPOSTOS
    # ========================================================

    df_impostos = pd.DataFrame(
        dados_impostos,
        columns=[
            "COD.REC.",
            "IMPOSTOS",
            "VENCTO",
            "VALOR IMPOSTO",
            "DEDUÇÃO NF",
            "TOTAL",
        ]
    )

    # ========================================================
    # FORMATA VALORES
    # ========================================================

    colunas_impostos = [
        "VALOR IMPOSTO",
        "DEDUÇÃO NF",
        "TOTAL",
    ]

    for coluna in colunas_impostos:

        df_impostos[coluna] = (
            df_impostos[coluna]
            .apply(formatar_reais)
        )

    # ========================================================
    # MOSTRA TABELA
    # ========================================================

    st.dataframe(
        df_impostos,
        width="stretch",
        hide_index=True
    )

    # ========================================================
    # TOTAL DOS IMPOSTOS
    # ========================================================

    total_impostos_tabela = (
        honorario_por_medico
        + total_iss_destacado
        + darf_gps_por_medico
        + cofins_a_pagar
        + pis_a_pagar
        + csll_a_pagar
        + ir_a_pagar
    )

    st.metric(
        "TOTAL",
        formatar_reais(total_impostos_tabela)
    )
