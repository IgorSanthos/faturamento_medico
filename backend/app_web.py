import streamlit as st
import pandas as pd
import tempfile
import os

from leitor_xml import extrair_dados_xml
from exportar_excel import gerar_planilha_notas

from calculos import (
    calcular_totais,
    gerar_demonstrativo
)

from formatacao import formatar_reais

from protocolo import gerar_protocolo

from paginas.medico import mostrar_pagina_medico


# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================

st.set_page_config(
    page_title="Gerador de Faturamento",
    page_icon="📊",
    layout="wide"
)


# ============================================================
# SESSION STATE
# ============================================================

if "pagina" not in st.session_state:
    st.session_state["pagina"] = "principal"


if "medico_selecionado" not in st.session_state:
    st.session_state["medico_selecionado"] = None


if "dados_extraidos" not in st.session_state:
    st.session_state["dados_extraidos"] = []


# ============================================================
# TÍTULO
# ============================================================

st.title("📊 Gerador de Faturamento")

st.write(
    "Selecione os arquivos XML das notas fiscais para gerar o relatório."
)


# ============================================================
# UPLOAD DOS XMLs
# ============================================================

arquivos_xml = st.file_uploader(
    "Selecione os arquivos XML",
    type=["xml"],
    accept_multiple_files=True
)


# ============================================================
# PROCESSAMENTO DOS XMLs
# ============================================================

if arquivos_xml:

    st.success(
        f"{len(arquivos_xml)} arquivo(s) selecionado(s)."
    )

    dados_extraidos = []


    for arquivo in arquivos_xml:

        try:

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".xml"
            ) as arquivo_temp:

                arquivo_temp.write(
                    arquivo.getvalue()
                )

                caminho_temp = arquivo_temp.name


            notas = extrair_dados_xml(
                caminho_temp
            )

            dados_extraidos.extend(
                notas
            )


            try:
                os.remove(caminho_temp)
            except:
                pass


        except Exception as e:

            st.error(
                f"Erro ao processar {arquivo.name}: {e}"
            )


    # Guarda os dados para a navegação entre páginas
    st.session_state["dados_extraidos"] = dados_extraidos


# ============================================================
# PÁGINA DO MÉDICO
# ============================================================

if (
    st.session_state["pagina"] == "medico"
    and st.session_state["dados_extraidos"]
    and st.session_state["medico_selecionado"]
):

    dados_extraidos = st.session_state["dados_extraidos"]

    # ========================================================
    # MÉDICOS
    # ========================================================

    medicos = sorted(
        set(
            nota.get("Medico", "")
            for nota in dados_extraidos
            if nota.get("Medico", "")
        )
    )

    quantidade_medicos = len(medicos)

    # ========================================================
    # VALORES TOTAIS
    # ========================================================

    honorario_total = st.session_state.get(
        "honorario_total",
        0.0
    )

    darf_gps_total = st.session_state.get(
        "darf_gps_total",
        0.0
    )

    # ========================================================
    # VALOR POR MÉDICO
    # ========================================================

    if quantidade_medicos > 0:

        honorario_por_medico = (
            honorario_total / quantidade_medicos
        )

        darf_gps_por_medico = (
            darf_gps_total / quantidade_medicos
        )

    else:

        honorario_por_medico = 0.0
        darf_gps_por_medico = 0.0

    # ========================================================
    # PÁGINA DO MÉDICO
    # ========================================================

    mostrar_pagina_medico(
        dados_extraidos,
        st.session_state["medico_selecionado"],
        honorario_por_medico=honorario_por_medico,
        darf_gps_por_medico=darf_gps_por_medico
    )

    st.stop()


# ============================================================
# PÁGINA PRINCIPAL
# ============================================================

if st.session_state["dados_extraidos"]:

    dados_extraidos = st.session_state[
        "dados_extraidos"
    ]


    # ========================================================
    # NOTAS FISCAIS
    # ========================================================

    st.subheader(
        "Notas fiscais encontradas"
    )


    df = pd.DataFrame(
        dados_extraidos
    )

    # ========================================================
    # VALORES TOTAIS
    # ========================================================

    st.subheader("💰 VALORES TOTAIS")

    col1, col2 = st.columns(2)

    with col1:
        honorario_total = st.number_input(
            "Honorário total",
            min_value=0.0,
            value=0.0,
            step=0.01,
            format="%.2f"
        )

    with col2:
        darf_gps_total = st.number_input(
            "DARF GPS total",
            min_value=0.0,
            value=0.0,
            step=0.01,
            format="%.2f"
        )

    st.session_state["honorario_total"] = honorario_total
    st.session_state["darf_gps_total"] = darf_gps_total

    # ========================================================
    # VALOR POR MÉDICO
    # ========================================================

    medicos = sorted(
        set(
            nota.get("Medico", "")
            for nota in dados_extraidos
            if nota.get("Medico", "")
        )
    )

    quantidade_medicos = len(medicos)

    if quantidade_medicos > 0:
        honorario_por_medico = (
            honorario_total / quantidade_medicos
        )

        darf_gps_por_medico = (
            darf_gps_total / quantidade_medicos
        )
    else:
        honorario_por_medico = 0.0
        darf_gps_por_medico = 0.0
    

    # ========================================================
    # CÁLCULOS
    # ========================================================

    totais = calcular_totais(df)


    total_faturamento = totais[
        "total_faturamento"
    ]

    total_iss = totais[
        "total_iss"
    ]

    total_inss = totais[
        "total_inss"
    ]

    total_pis = totais[
        "total_pis"
    ]

    total_cofins = totais[
        "total_cofins"
    ]

    total_csll = totais[
        "total_csll"
    ]

    total_ir = totais[
        "total_ir"
    ]



    # ========================================================
    # FORMATAÇÃO DA TABELA
    # ========================================================

    colunas_monetarias = [
        "ValorTotal",
        "ValorIr",
        "ValorInss",
        "ValorIss",
        "SomaPisCofinsCsll",
        "ValorPis",
        "ValorCofins",
        "ValorCsll",
        "TotalImpostos"
    ]


    for coluna in colunas_monetarias:

        if coluna in df.columns:

            df[coluna] = df[
                coluna
            ].apply(formatar_reais)


    # ========================================================
    # TABELA DE NOTAS
    # ========================================================

    st.dataframe(
        df,
        width="stretch",
        hide_index=True
    )


    st.divider()


    # ========================================================
    # GERAR EXCEL
    # ========================================================

    if st.button(
        "📥 Gerar Excel",
        width="stretch"
    ):

        caminho_excel = os.path.join(
            tempfile.gettempdir(),
            "Relatorio_Notas_Fiscais.xlsx"
        )


        try:

            gerar_planilha_notas(
                dados_extraidos,
                caminho_saida=caminho_excel,
                honorario_por_medico=honorario_por_medico,
                darf_gps_por_medico=darf_gps_por_medico
            )


            with open(
                caminho_excel,
                "rb"
            ) as arquivo:

                st.download_button(
                    label="⬇️ Baixar Excel",
                    data=arquivo,
                    file_name="Relatorio_Notas_Fiscais.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    width="stretch"
                )


            st.success(
                "Excel gerado com sucesso!"
            )


        except Exception as e:

            st.error(
                f"Erro ao gerar o Excel: {e}"
            )


    st.divider()


    # ========================================================
    # DEMONSTRATIVO DE IMPOSTOS
    # ========================================================

    st.subheader("📊 DEMONSTRATIVO DE IMPOSTOS")

    demonstrativo = gerar_demonstrativo(
        dados_extraidos,
        honorario_por_medico=honorario_por_medico,
        darf_gps_por_medico=darf_gps_por_medico
    )

    # Criamos uma cópia para exibição formatada em Reais, mantendo a original ou valores limpos se necessário,
    # mas para o selectbox/dataframe interativo, podemos exibir já formatado ou formatar visualmente.
    demonstrativo_exibicao = demonstrativo.copy()
    demonstrativo_exibicao["Valor dos Impostos"] = demonstrativo_exibicao["Valor dos Impostos"].apply(formatar_reais)

    # Exibimos a tabela interativa permitindo seleção de linha
    evento_selecao = st.dataframe(
        demonstrativo_exibicao,
        width="stretch",
        hide_index=True,
        selection_mode="single-row",
        on_select="rerun",
        key="tabela_demonstrativo"
    )

    # Verifica se o usuário selecionou alguma linha na tabela
    linhas_selecionadas = evento_selecao.get("selection", {}).get("rows", [])

    if linhas_selecionadas:
        indice_selecionado = linhas_selecionadas[0]
        medico_clicado = demonstrativo.iloc[indice_selecionado]["Médico"]
        
        # Evita que clique na linha "TOTAL" abra página de médico
        if medico_clicado != "TOTAL":
            st.session_state["medico_selecionado"] = medico_clicado
            st.session_state["pagina"] = "medico"
            st.rerun()

    st.divider()


    # ========================================================
    # PROTOCOLO
    # ========================================================

    st.subheader(
        "📋 PROTOCOLO DE IMPOSTOS ENVIADOS - AGOSTO/2026"
    )


    df_protocolo = gerar_protocolo(

        total_faturamento=total_faturamento,

        total_iss=total_iss,

        total_inss=total_inss,

        total_pis=total_pis,

        total_cofins=total_cofins,

        total_csll=total_csll,

        total_ir=total_ir
    )


    # ========================================================
    # FORMATAÇÃO DO PROTOCOLO
    # ========================================================

    df_protocolo[
        "Valor R$"
    ] = df_protocolo[
        "Valor R$"
    ].apply(
        formatar_reais
    )


    st.dataframe(
        df_protocolo,
        width="stretch",
        hide_index=True
    )


    # ========================================================
    # DATA DO ENVIO
    # ========================================================

    st.write(
        "📅 Data do envio do Faturamento e Impostos:"
    )


    data_envio = st.date_input(
        "Data do envio",
        label_visibility="collapsed"
    )


# ============================================================
# NENHUM XML
# ============================================================

else:

    st.info(
        "Selecione os arquivos XML para iniciar."
    )