import os
import tempfile
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import pandas as pd
from calculos import calcular_totais, gerar_demonstrativo
from exportar_excel import gerar_planilha_notas
from leitor_geral import ler_arquivos
from protocolo import gerar_protocolo

app = FastAPI(title="Faturamento Médico API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# TESTE DA API
# ============================================================


@app.get("/")
def inicio():
    return {
        "status": "online",
        "sistema": "Faturamento Médico API"
    }


# ============================================================
# PROCESSAR ARQUIVOS
# ============================================================


@app.post("/notas/processar")
async def processar_notas(
    arquivos: list[UploadFile] = File(...)
):
    dados_extraidos = []
    caminhos_temp = []

    try:
        # ====================================================
        # SALVAR TODOS OS ARQUIVOS TEMPORARIAMENTE
        # ====================================================

        for arquivo in arquivos:
            conteudo = await arquivo.read()
            extensao = os.path.splitext(
                arquivo.filename
            )[1]

            if not extensao:
                extensao = ".xml"

            arquivo_temp = tempfile.NamedTemporaryFile(
                delete=False,
                suffix=extensao
            )

            arquivo_temp.write(conteudo)
            arquivo_temp.close()

            caminhos_temp.append(
                arquivo_temp.name
            )

        # ====================================================
        # PROCESSAR TODOS OS ARQUIVOS
        # ====================================================

        notas = ler_arquivos(
            caminhos_temp
        )

        dados_extraidos.extend(notas)

    finally:
        # ====================================================
        # APAGAR ARQUIVOS TEMPORÁRIOS
        # ====================================================

        for caminho in caminhos_temp:
            if os.path.exists(caminho):
                os.remove(caminho)

    return {
        "quantidade": len(dados_extraidos),
        "dados": dados_extraidos
    }


# ============================================================
# CALCULAR FATURAMENTO
# ============================================================


@app.post("/faturamento/calcular")
async def calcular_faturamento(
    dados: dict
):
    dados_extraidos = dados.get(
        "dados",
        []
    )

    honorario_total = float(
        dados.get(
            "honorario_total",
            0
        )
    )

    darf_gps_total = float(
        dados.get(
            "darf_gps_total",
            0
        )
    )

    # ========================================================
    # NENHUM DADO
    # ========================================================

    if not dados_extraidos:
        return {
            "totais": {
                "total_faturamento": 0,
                "total_iss": 0,
                "total_inss": 0,
                "total_pis": 0,
                "total_cofins": 0,
                "total_csll": 0,
                "total_ir": 0,
                "total_impostos": 0,
            },
            "demonstrativo": [],
            "protocolo": [],
        }

    # ========================================================
    # DATAFRAME
    # ========================================================

    df = pd.DataFrame(
        dados_extraidos
    )

    # ========================================================
    # FILTRAR NOTAS VÁLIDAS
    #
    # Notas canceladas continuam em dados_extraidos
    # para aparecerem na tela, mas não participam
    # dos cálculos.
    # ========================================================

    if "SituacaoNota" in df.columns:

        df_validas = df[
            df["SituacaoNota"]
            .fillna("")
            .astype(str)
            .str.upper()
            .str.strip() != "C"
        ].copy()

    else:

        df_validas = df.copy()

    # ========================================================
    # QUANTIDADE DE MÉDICOS
    #
    # Somente médicos com notas válidas entram na divisão.
    # ========================================================

    medicos = sorted(
        set(
            nota.get("Medico", "")
            for nota in dados_extraidos
            if str(
                nota.get(
                    "SituacaoNota",
                    ""
                )
            ).upper().strip() != "C"
        )
    )

    quantidade_medicos = len(
        medicos
    )

    # ========================================================
    # VALORES POR MÉDICO
    # ========================================================

    if quantidade_medicos > 0:

        honorario_por_medico = (
            honorario_total
            / quantidade_medicos
        )

        darf_gps_por_medico = (
            darf_gps_total
            / quantidade_medicos
        )

    else:

        honorario_por_medico = 0.0
        darf_gps_por_medico = 0.0

    # ========================================================
    # TOTAIS
    # ========================================================

    totais = calcular_totais(
        df
    )

    # ========================================================
    # DEMONSTRATIVO
    # ========================================================

    demonstrativo, totais_a_pagar = (
        gerar_demonstrativo(
            dados_extraidos,
            honorario_por_medico=honorario_por_medico,
            darf_gps_por_medico=darf_gps_por_medico,
        )
    )

    # ========================================================
    # PROTOCOLO
    # ========================================================

    protocolo = gerar_protocolo(
        dados_extraidos=dados_extraidos,
        total_faturamento=totais[
            "total_faturamento"
        ],
        total_iss=totais[
            "total_iss"
        ],
        total_inss=totais[
            "total_inss"
        ],
        honorario_total=honorario_total
    )

    # ========================================================
    # CONVERTER DEMONSTRATIVO PARA JSON
    # ========================================================

    demonstrativo_json = (
        demonstrativo
        .fillna("")
        .to_dict(
            orient="records"
        )
    )

    # ========================================================
    # CONVERTER PROTOCOLO PARA JSON
    # ========================================================

    protocolo_json = (
        protocolo
        .fillna("")
        .to_dict(
            orient="records"
        )
    )

    # ========================================================
    # RETORNO
    # ========================================================

    return {
        "totais": totais,

        "honorario_total":
            honorario_total,

        "darf_gps_total":
            darf_gps_total,

        "honorario_por_medico":
            honorario_por_medico,

        "darf_gps_por_medico":
            darf_gps_por_medico,

        "quantidade_medicos":
            quantidade_medicos,

        "medicos":
            medicos,

        "demonstrativo":
            demonstrativo_json,

        "protocolo":
            protocolo_json,
    }


# ============================================================
# GERAR EXCEL
# ============================================================


@app.post("/faturamento/excel")
async def gerar_excel(
    dados: dict
):
    dados_extraidos = dados.get(
        "dados",
        []
    )

    honorario_por_medico = float(
        dados.get(
            "honorario_por_medico",
            0
        )
    )

    darf_gps_por_medico = float(
        dados.get(
            "darf_gps_por_medico",
            0
        )
    )

    # ========================================================
    # NENHUM DADO
    # ========================================================

    if not dados_extraidos:
        return {
            "erro":
                "Nenhuma nota fiscal foi informada."
        }

    # ========================================================
    # ARQUIVO TEMPORÁRIO
    # ========================================================

    caminho_temp = (
        tempfile
        .NamedTemporaryFile(
            delete=False,
            suffix=".xlsx"
        )
        .name
    )

    try:

        # ====================================================
        # GERAR PLANILHA
        # ====================================================

        gerar_planilha_notas(
            dados_extraidos,
            caminho_saida=caminho_temp,
            honorario_por_medico=
                honorario_por_medico,
            darf_gps_por_medico=
                darf_gps_por_medico,
        )

        # ====================================================
        # DOWNLOAD
        # ====================================================

        return FileResponse(
            caminho_temp,
            media_type=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),
            filename=
                "Relatorio_Faturamento.xlsx",
        )

    except Exception as e:

        if os.path.exists(
            caminho_temp
        ):
            os.remove(
                caminho_temp
            )

        return {
            "erro": str(e)
        }
