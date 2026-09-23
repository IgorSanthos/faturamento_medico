import pandas as pd


def gerar_protocolo(
    dados_extraidos,
    total_faturamento=0,
    total_iss=0,
    total_inss=0,
    honorario_total=0,
):
  """Gera o protocolo de impostos.

  Base de cálculo:
      Total do faturamento bruto.

  Fórmulas:
      PIS    = faturamento * 0,65% - PIS destacado
      COFINS = faturamento * 3,00% - COFINS destacado
      CSLL   = faturamento * 1,08% - CSLL destacado
      IRPJ   = faturamento * 1,20% - IR destacado

  Regra:
      Se o resultado de algum imposto for negativo,
      o protocolo apresenta R$ 0,00.
  """

  df = pd.DataFrame(dados_extraidos)

  # ============================================================
  # GARANTIR COLUNAS
  # ============================================================

  colunas_impostos = ["ValorPis", "ValorCofins", "ValorCsll", "ValorIr"]

  for coluna in colunas_impostos:
    if coluna not in df.columns:
      df[coluna] = 0

    df[coluna] = pd.to_numeric(df[coluna], errors="coerce").fillna(0)

  # ============================================================
  # BASE DE CÁLCULO
  # ============================================================

  base_calculo = float(total_faturamento or 0)

  # ============================================================
  # IMPOSTOS DESTACADOS NAS NOTAS
  # ============================================================

  pis_destacado = round(df["ValorPis"].sum(), 2)
  cofins_destacado = round(df["ValorCofins"].sum(), 2)
  csll_destacado = round(df["ValorCsll"].sum(), 2)
  ir_destacado = round(df["ValorIr"].sum(), 2)

  # ============================================================
  # IMPOSTOS A PAGAR
  # ============================================================

  pis_a_pagar = max(round((base_calculo * 0.0065) - pis_destacado, 2), 0)

  cofins_a_pagar = max(round((base_calculo * 0.03) - cofins_destacado, 2), 0)

  csll_a_pagar = max(round((base_calculo * 0.0108) - csll_destacado, 2), 0)

  ir_a_pagar = max(round((base_calculo * 0.012) - ir_destacado, 2), 0)

  # ============================================================
  # OUTROS VALORES
  # ============================================================

  honorario = round(float(honorario_total or 0), 2)

  iss = round(float(total_iss or 0), 2)

  darf_gps = round(float(total_inss or 0), 2)

  # ============================================================
  # TOTAL
  # ============================================================

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

  # ============================================================
  # PROTOCOLO
  # ============================================================

  linhas = [
      {"Descrição": "Honorário", "Vencimento": "25/09/2026", "Valor R$": honorario},
      {"Descrição": "ISS", "Vencimento": "10/09/2026", "Valor R$": iss},
      {"Descrição": "DARF / GPS", "Vencimento": "18/09/2026", "Valor R$": darf_gps},
      {
          "Descrição": "COFINS a pagar",
          "Vencimento": "25/09/2026",
          "Valor R$": cofins_a_pagar,
      },
      {
          "Descrição": "PIS a pagar",
          "Vencimento": "25/09/2026",
          "Valor R$": pis_a_pagar,
      },
      {
          "Descrição": "CSLL a pagar",
          "Vencimento": "30/09/2026",
          "Valor R$": csll_a_pagar,
      },
      {
          "Descrição": "IRPJ a pagar",
          "Vencimento": "30/09/2026",
          "Valor R$": ir_a_pagar,
      },
      {"Descrição": "TOTAL", "Vencimento": "", "Valor R$": total},
  ]

  return pd.DataFrame(linhas)