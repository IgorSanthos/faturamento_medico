import { useState } from 'react'
import { createFileRoute, useNavigate } from '@tanstack/react-router'

import { AppHeader } from '../components/AppHeader'
import { UploadPanel } from '../components/UploadPanel'

type Nota = {
  Prestador?: string
  DataEmissao?: string
  NumeroNF?: string
  TomadorServico?: string
  ValorTotal?: number
  ValorIr?: number
  ValorInss?: number
  ValorIss?: number
  SomaPisCofinsCsll?: number
  ValorPis?: number
  ValorCofins?: number
  ValorCsll?: number
  TotalImpostos?: number
  Medico?: string
}

export const Route = createFileRoute('/')({
  component: HomePage,
})

function HomePage() {
  const navigate = useNavigate()

  const [notas, setNotas] = useState<Nota[]>([])

  const [honorarioTotal, setHonorarioTotal] = useState(0)

  const [darfGpsTotal, setDarfGpsTotal] = useState(0)

  const [calculos, setCalculos] = useState<any>(null)

  // const protocolo = calculos?.protocolo || []

  const [calculando, setCalculando] = useState(false)

  const [erroCalculo, setErroCalculo] = useState('')

  function formatarReais(valor: number = 0) {
    return valor.toLocaleString('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    })
  }

  function formatarData(data?: string) {
    if (!data) return '-'

    const partes = data.split('-')

    if (partes.length === 3) {
      return `${partes[2]}/${partes[1]}/${partes[0]}`
    }

    return data
  }
  async function calcularFaturamento(
    dadosNotas: Nota[],
    honorario: number,
    darfGps: number
  ) {
    setCalculando(true)
    setErroCalculo('')

    try {
      const resposta = await fetch(
        'http://127.0.0.1:8000/faturamento/calcular',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            dados: dadosNotas,
            honorario_total: honorario,
            darf_gps_total: darfGps,
          }),
        }
      )

      if (!resposta.ok) {
        throw new Error(
          'Erro ao calcular o faturamento.'
        )
      }

      const resultado = await resposta.json()

      setCalculos(resultado)

    } catch (error) {
      console.error(error)

      setErroCalculo(
        'Não foi possível calcular o faturamento.'
      )

    } finally {
      setCalculando(false)
    }
  }

  const faturamento =
    calculos?.totais?.total_faturamento || 0

  const iss =
    calculos?.totais?.total_iss || 0

  const inss =
    calculos?.totais?.total_inss || 0

  const pis =
    calculos?.totais?.total_pis || 0

  const cofins =
    calculos?.totais?.total_cofins || 0

  const csll =
    calculos?.totais?.total_csll || 0

  const ir =
    calculos?.totais?.total_ir || 0

  // const medicos = Array.from(
  //   new Set(
  //     notas
  //       .map((nota) => nota.Medico)
  //       .filter(Boolean)
  //   )
  // ).sort()
  async function gerarExcel() {
    try {
      const resposta = await fetch(
        'http://127.0.0.1:8000/faturamento/excel',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            dados: notas,
            honorario_por_medico:
              calculos?.honorario_por_medico || 0,
            darf_gps_por_medico:
              calculos?.darf_gps_por_medico || 0,
          }),
        }
      )

      if (!resposta.ok) {
        throw new Error(
          'Erro ao gerar o Excel.'
        )
      }

      const blob = await resposta.blob()

      const url = window.URL.createObjectURL(blob)

      const link = document.createElement('a')

      link.href = url
      link.download = 'Relatorio_Faturamento.xlsx'

      document.body.appendChild(link)

      link.click()

      link.remove()

      window.URL.revokeObjectURL(url)

    } catch (error) {

      console.error(error)

      alert(
        'Não foi possível gerar o Excel.'
      )
    }
  }
  return (
    <div className="min-h-screen bg-slate-50">
      <AppHeader />

      <main className="mx-auto max-w-7xl space-y-8 px-6 py-8">

        {/* =====================================================
            BREADCRUMB
        ===================================================== */}

        <div className="flex items-center gap-2 text-sm">
          <span className="font-medium text-slate-400">
            Dashboard
          </span>

          <span className="text-slate-300">
            /
          </span>

          <span className="font-semibold text-slate-700">
            Faturamento
          </span>
        </div>

        {/* =====================================================
            IMPORTAR NOTAS FISCAIS
        ===================================================== */}

        <UploadPanel
          onNotasProcessadas={(dados) => {
            setNotas(dados)

            calcularFaturamento(
              dados,
              honorarioTotal,
              darfGpsTotal
            )
          }}
        />
          {/* =================================================
                GERAR EXCEL
          ================================================= */}

            <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">

              <div className="mb-5">
                <h2 className="text-xl font-semibold text-slate-900">
                  Gerar Excel
                </h2>

                <p className="mt-1 text-sm text-slate-500">
                  Gere a planilha completa com os dados do faturamento.
                </p>
              </div>

              <div className="flex flex-col gap-3 sm:flex-row">

                <button
                  type="button"
                  onClick={gerarExcel}
                  disabled={!calculos}
                  className="rounded-xl bg-blue-900 px-6 py-3 text-sm font-semibold text-white transition hover:bg-blue-800 disabled:cursor-not-allowed disabled:bg-slate-300"
                >
                  ⬇️ Gerar Excel
                </button>

              </div>

            </section>
        {/* =====================================================
            CONTEÚDO APÓS IMPORTAÇÃO
        ===================================================== */}

        {notas.length > 0 && (
          <>
            {/* =================================================
                NOTAS FISCAIS
            ================================================= */}

            <section>
              <div className="mb-4">
                <h2 className="text-xl font-semibold text-slate-900">
                  Notas Fiscais
                </h2>

                <p className="mt-1 text-sm text-slate-500">
                  {notas.length} nota(s) fiscal(is) encontrada(s).
                </p>
              </div>

              <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">

                {/* TABELA COM ROLAGEM INTERNA */}

                <div className="max-h-[360px] overflow-auto">

                  <table className="min-w-[1100px] w-full text-left text-sm">

                    <thead className="sticky top-0 z-10 bg-slate-100">
                      <tr className="border-b border-slate-200">

                        <th className="whitespace-nowrap px-5 py-4 font-semibold text-slate-600">
                          Data
                        </th>

                        <th className="whitespace-nowrap px-5 py-4 font-semibold text-slate-600">
                          Cliente
                        </th>

                        <th className="whitespace-nowrap px-5 py-4 font-semibold text-slate-600">
                          NF
                        </th>

                        <th className="whitespace-nowrap px-5 py-4 text-right font-semibold text-slate-600">
                          Valor
                        </th>

                        <th className="whitespace-nowrap px-5 py-4 text-right font-semibold text-slate-600">
                          IR
                        </th>

                        <th className="whitespace-nowrap px-5 py-4 text-right font-semibold text-slate-600">
                          ISS
                        </th>

                        <th className="whitespace-nowrap px-5 py-4 text-right font-semibold text-slate-600">
                          INSS
                        </th>

                        <th className="whitespace-nowrap px-5 py-4 text-right font-semibold text-slate-600">
                          PIS/COFINS
                        </th>

                        <th className="whitespace-nowrap px-5 py-4 text-right font-semibold text-slate-600">
                          CSLL
                        </th>

                        <th className="whitespace-nowrap px-5 py-4 font-semibold text-slate-600">
                          Médico
                        </th>

                      </tr>
                    </thead>

                    <tbody>

                      {notas.map((nota, index) => (
                        <tr
                          key={index}
                          className="border-b border-slate-100 last:border-0 hover:bg-slate-50"
                        >

                          <td className="whitespace-nowrap px-5 py-3 text-slate-600">
                            {formatarData(nota.DataEmissao)}
                          </td>

                          <td className="max-w-[240px] truncate px-5 py-3 text-slate-700">
                            {nota.TomadorServico || '-'}
                          </td>

                          <td className="whitespace-nowrap px-5 py-3 text-slate-600">
                            {nota.NumeroNF || '-'}
                          </td>

                          <td className="whitespace-nowrap px-5 py-3 text-right font-medium text-slate-800">
                            {formatarReais(nota.ValorTotal)}
                          </td>

                          <td className="whitespace-nowrap px-5 py-3 text-right text-slate-600">
                            {formatarReais(nota.ValorIr)}
                          </td>

                          <td className="whitespace-nowrap px-5 py-3 text-right text-slate-600">
                            {formatarReais(nota.ValorIss)}
                          </td>

                          <td className="whitespace-nowrap px-5 py-3 text-right text-slate-600">
                            {formatarReais(nota.ValorInss)}
                          </td>

                          <td className="whitespace-nowrap px-5 py-3 text-right text-slate-600">
                            {formatarReais(
                              (nota.ValorPis || 0) +
                              (nota.ValorCofins || 0)
                            )}
                          </td>

                          <td className="whitespace-nowrap px-5 py-3 text-right text-slate-600">
                            {formatarReais(nota.ValorCsll)}
                          </td>

                          <td className="max-w-[220px] truncate px-5 py-3 font-medium text-slate-700">
                            {nota.Medico || '-'}
                          </td>

                        </tr>
                      ))}

                    </tbody>

                  </table>

                </div>

                {/* RODAPÉ DA TABELA */}

                <div className="flex items-center justify-between border-t border-slate-100 bg-slate-50 px-5 py-3">

                  <span className="text-xs text-slate-500">
                    {notas.length} registro(s)
                  </span>

                  <span className="text-xs text-slate-400">
                    Role dentro da tabela para visualizar mais registros
                  </span>

                </div>

              </div>
            </section>

            {/* =================================================
                RESUMO DOS VALORES
            ================================================= */}

            <section>

              <div className="mb-4">
                <h2 className="text-xl font-semibold text-slate-900">
                  Valores Totais
                </h2>

                <p className="mt-1 text-sm text-slate-500">
                  Resumo dos valores encontrados nas notas fiscais.
                </p>
              </div>

              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">

                <div className="rounded-2xl border border-blue-200 bg-blue-900 p-5 shadow-sm">
                  <p className="text-sm font-medium text-blue-100">
                    Faturamento
                  </p>

                  <p className="mt-2 text-2xl font-bold text-white">
                    {formatarReais(faturamento)}
                  </p>
                </div>

                <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
                  <p className="text-sm font-medium text-slate-500">
                    ISS
                  </p>

                  <p className="mt-2 text-2xl font-bold text-slate-900">
                    {formatarReais(iss)}
                  </p>
                </div>

                <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
                  <p className="text-sm font-medium text-slate-500">
                    INSS
                  </p>

                  <p className="mt-2 text-2xl font-bold text-slate-900">
                    {formatarReais(inss)}
                  </p>
                </div>

                <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
                  <p className="text-sm font-medium text-slate-500">
                    PIS
                  </p>

                  <p className="mt-2 text-2xl font-bold text-slate-900">
                    {formatarReais(pis)}
                  </p>
                </div>

                <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
                  <p className="text-sm font-medium text-slate-500">
                    COFINS
                  </p>

                  <p className="mt-2 text-2xl font-bold text-slate-900">
                    {formatarReais(cofins)}
                  </p>
                </div>

                <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
                  <p className="text-sm font-medium text-slate-500">
                    CSLL
                  </p>

                  <p className="mt-2 text-2xl font-bold text-slate-900">
                    {formatarReais(csll)}
                  </p>
                </div>

                <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
                  <p className="text-sm font-medium text-slate-500">
                    IR
                  </p>

                  <p className="mt-2 text-2xl font-bold text-slate-900">
                    {formatarReais(ir)}
                  </p>
                </div>

              </div>

            </section>
            
            <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">

              <div className="mb-5">
                <h2 className="text-xl font-semibold text-slate-900">
                  Valores para cálculo
                </h2>

                <p className="mt-1 text-sm text-slate-500">
                  Informe os valores utilizados no cálculo do demonstrativo.
                </p>
              </div>

              <div className="grid gap-5 md:grid-cols-2">

                <div>
                  <label className="mb-2 block text-sm font-medium text-slate-700">
                    Honorário total
                  </label>

                  <input
                    type="number"
                    min="0"
                    step="0.01"
                    value={honorarioTotal}
                    onChange={(event) => {
                      const valor = Number(event.target.value)

                      setHonorarioTotal(valor)

                      calcularFaturamento(
                        notas,
                        valor,
                        darfGpsTotal
                      )
                    }}
                    className="w-full rounded-xl border border-slate-300 px-4 py-3 text-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                  />
                </div>

                <div>
                  <label className="mb-2 block text-sm font-medium text-slate-700">
                    DARF GPS total
                  </label>

                  <input
                    type="number"
                    min="0"
                    step="0.01"
                    value={darfGpsTotal}
                    onChange={(event) => {
                      const valor = Number(event.target.value)

                      setDarfGpsTotal(valor)

                      calcularFaturamento(
                        notas,
                        honorarioTotal,
                        valor
                      )
                    }}
                    className="w-full rounded-xl border border-slate-300 px-4 py-3 text-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                  />
                </div>

              </div>

              {calculando && (
                <p className="mt-4 text-sm text-blue-600">
                  Calculando...
                </p>
              )}

              {erroCalculo && (
                <div className="mt-4 rounded-xl border border-red-200 bg-red-50 px-4 py-3">
                  <p className="text-sm font-medium text-red-700">
                    {erroCalculo}
                  </p>
                </div>
              )}

            </section>

            {/* =================================================
                DEMONSTRATIVO DE IMPOSTOS
            ================================================= */}

            <section>

              <div className="mb-4">
                <h2 className="text-xl font-semibold text-slate-900">
                  Demonstrativo de Impostos
                </h2>

                <p className="mt-1 text-sm text-slate-500">
                  Demonstrativo dos impostos por médico.
                </p>
              </div>

              <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">

                <div className="overflow-x-auto">

                  <table className="w-full min-w-[700px] text-left text-sm">

                    <thead className="bg-slate-100">

                      <tr className="border-b border-slate-200">

                        <th className="px-6 py-4 font-semibold text-slate-600">
                          Médico
                        </th>

                        <th className="px-6 py-4 text-right font-semibold text-slate-600">
                          Impostos
                        </th>

                        <th className="px-6 py-4 text-center font-semibold text-slate-600">
                          Ação
                        </th>

                      </tr>

                    </thead>

                    <tbody>

                      {(calculos?.demonstrativo || [])
                        .filter(
                          (linha: any) =>
                            linha['Médico'] !== 'TOTAL'
                        )
                        .map(
                          (linha: any, index: number) => (

                            <tr
                              key={index}
                              className="border-b border-slate-100"
                            >

                              <td className="px-6 py-4 font-medium text-slate-700">
                                {linha['Médico']}
                              </td>

                              <td className="px-6 py-4 text-right font-semibold text-slate-800">
                                {formatarReais(
                                  Number(
                                    linha['Valor dos Impostos'] || 0
                                  )
                                )}
                              </td>

                              <td className="px-6 py-4 text-center">

                                <button
                                  type="button"
                                  onClick={() => {
                                  sessionStorage.setItem(
                                    'notas_faturamento',
                                    JSON.stringify(notas)
                                  )

                                  sessionStorage.setItem(
                                    'honorario_por_medico',
                                    String(
                                      calculos?.honorario_por_medico || 0
                                    )
                                  )

                                  sessionStorage.setItem(
                                    'darf_gps_por_medico',
                                    String(
                                      calculos?.darf_gps_por_medico || 0
                                    )
                                  )

                                  navigate({
                                    to: '/medico',
                                    search: {
                                      medico: linha['Médico'],
                                    },
                                  })

                                }}
                                  className="rounded-lg bg-blue-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-800"
                                >
                                  Ver detalhes
                                </button>

                              </td>

                            </tr>

                          )
                        )}

                      <tr className="bg-slate-50">

                        <td className="px-6 py-4 font-bold text-slate-900">
                          TOTAL
                        </td>

                        <td className="px-6 py-4 text-right font-bold text-slate-900">
                          {formatarReais(
                            Number(
                              calculos?.demonstrativo?.find(
                                (item: any) =>
                                  item['Médico'] === 'TOTAL'
                              )?.['Valor dos Impostos'] || 0
                            )
                          )}
                        </td>

                        <td></td>

                      </tr>

                    </tbody>

                  </table>

                </div>

              </div>

            </section>

            {/* =================================================
                PROTOCOLO
            ================================================= */}

            <section>

              <div className="mb-4">
                <h2 className="text-xl font-semibold text-slate-900">
                  Protocolo de Impostos Enviados - Agosto/2026
                </h2>

                <p className="mt-1 text-sm text-slate-500">
                  Controle dos documentos e valores enviados.
                </p>
              </div>

              <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">

                <div className="overflow-x-auto">

                  <table className="w-full min-w-[700px] text-left text-sm">

                    <thead className="bg-slate-100">

                      <tr className="border-b border-slate-200">

                        <th className="px-6 py-4 font-semibold text-slate-600">
                          Descrição
                        </th>

                        <th className="px-6 py-4 font-semibold text-slate-600">
                          Vencimento
                        </th>

                        <th className="px-6 py-4 text-right font-semibold text-slate-600">
                          Valor R$
                        </th>

                      </tr>

                    </thead>

                    <tbody>

                      <tr className="border-b border-slate-100">
                        <td className="px-6 py-4 text-slate-700">
                          Planilha de Faturamento 08/2026
                        </td>

                        <td className="px-6 py-4 text-slate-500">
                          -
                        </td>

                        <td className="px-6 py-4 text-right font-medium text-slate-800">
                          {formatarReais(faturamento)}
                        </td>
                      </tr>

                      <tr className="border-b border-slate-100">
                        <td className="px-6 py-4 text-slate-700">
                          Guia de ISS 08/2026
                        </td>

                        <td className="px-6 py-4 text-slate-500">
                          10/09/2026
                        </td>

                        <td className="px-6 py-4 text-right font-medium text-slate-800">
                          {formatarReais(iss)}
                        </td>
                      </tr>

                      <tr className="border-b border-slate-100">
                        <td className="px-6 py-4 text-slate-700">
                          Darf GPS 08/2026
                        </td>

                        <td className="px-6 py-4 text-slate-500">
                          18/09/2026
                        </td>

                        <td className="px-6 py-4 text-right font-medium text-slate-800">
                          {formatarReais(inss)}
                        </td>
                      </tr>

                      <tr className="border-b border-slate-100">
                        <td className="px-6 py-4 text-slate-700">
                          Boleto de Honorários 08/2026
                        </td>

                        <td className="px-6 py-4 text-slate-500">
                          25/09/2026
                        </td>

                        <td className="px-6 py-4 text-right font-medium text-slate-800">
                          R$ 1.621,00
                        </td>
                      </tr>

                      <tr className="border-b border-slate-100">
                        <td className="px-6 py-4 text-slate-700">
                          Darf Pis 08/2026
                        </td>

                        <td className="px-6 py-4 text-slate-500">
                          25/09/2026
                        </td>

                        <td className="px-6 py-4 text-right font-medium text-slate-800">
                          {formatarReais(pis)}
                        </td>
                      </tr>

                      <tr className="border-b border-slate-100">
                        <td className="px-6 py-4 text-slate-700">
                          Darf Cofins 08/2026
                        </td>

                        <td className="px-6 py-4 text-slate-500">
                          25/09/2026
                        </td>

                        <td className="px-6 py-4 text-right font-medium text-slate-800">
                          {formatarReais(cofins)}
                        </td>
                      </tr>

                      <tr className="border-b border-slate-100">
                        <td className="px-6 py-4 text-slate-700">
                          Darf CSLL 08/2026
                        </td>

                        <td className="px-6 py-4 text-slate-500">
                          30/09/2026
                        </td>

                        <td className="px-6 py-4 text-right font-medium text-slate-800">
                          {formatarReais(csll)}
                        </td>
                      </tr>

                      <tr className="border-b border-slate-100">
                        <td className="px-6 py-4 text-slate-700">
                          Darf IRPJ 08/2026
                        </td>

                        <td className="px-6 py-4 text-slate-500">
                          30/09/2026
                        </td>

                        <td className="px-6 py-4 text-right font-medium text-slate-800">
                          {formatarReais(ir)}
                        </td>
                      </tr>

                      <tr className="bg-slate-50">

                        <td className="px-6 py-4 font-bold text-slate-900">
                          TOTAL
                        </td>

                        <td></td>

                        <td className="px-6 py-4 text-right font-bold text-slate-900">
                          {formatarReais(
                            faturamento +
                            iss +
                            inss +
                            1621 +
                            pis +
                            cofins +
                            csll +
                            ir
                          )}
                        </td>

                      </tr>

                    </tbody>

                  </table>

                </div>

              </div>

            </section>

            {/* =================================================
                DATA DE ENVIO
            ================================================= */}

            <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">

              <h2 className="text-lg font-semibold text-slate-900">
                📅 Data do envio do Faturamento e Impostos
              </h2>

              <p className="mt-1 text-sm text-slate-500">
                Informe a data em que o faturamento e os impostos foram enviados.
              </p>

              <div className="mt-5 max-w-sm">

                <label className="mb-2 block text-sm font-medium text-slate-700">
                  Data do envio
                </label>

                <input
                  type="date"
                  className="w-full rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm text-slate-700 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                />

              </div>

            </section>

          </>
        )}

        {/* =====================================================
            ESTADO INICIAL
        ===================================================== */}

        {notas.length === 0 && (
          <div className="rounded-2xl border border-dashed border-slate-300 bg-white px-6 py-10 text-center">

            <div className="text-3xl">
              📄
            </div>

            <h3 className="mt-3 text-base font-semibold text-slate-800">
              Nenhuma nota fiscal carregada
            </h3>

            <p className="mt-1 text-sm text-slate-500">
              Selecione os arquivos XML acima para iniciar o faturamento.
            </p>

          </div>
        )}

      </main>
    </div>
  )
}