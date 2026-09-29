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
  ValorPisRetido?: number
  ValorCofinsRetido?: number
  ValorCsllRetido?: number
  ValorPccRetido?: number
  TotalImpostos?: number
  Medico?: string
  SituacaoNota?: string
}

export const Route = createFileRoute('/')({
  component: HomePage,
})

function HomePage() {
  const navigate = useNavigate()

  const [notas, setNotas] = useState<Nota[]>(() => {
    const dadosSalvos = sessionStorage.getItem('notas_faturamento')

    if (!dadosSalvos) return []

    try {
      return JSON.parse(dadosSalvos)
    } catch {
      return []
    }
  })

  const [honorarioTotal, setHonorarioTotal] = useState(() =>
    Number(sessionStorage.getItem('honorario_total') || 0)
  )

  const [darfGpsTotal, setDarfGpsTotal] = useState(() =>
    Number(sessionStorage.getItem('darf_gps_total') || 0)
  )

  const [calculos, setCalculos] = useState<any>(() => {
    const calculosSalvos = sessionStorage.getItem('calculos_faturamento')

    if (!calculosSalvos) return null

    try {
      return JSON.parse(calculosSalvos)
    } catch {
      return null
    }
  })

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

    const somenteData = data.split('T')[0].split(' ')[0]
    const partes = somenteData.split('-')

    if (partes.length === 3) {
      return `${partes[2]}/${partes[1]}/${partes[0]}`
    }

    return somenteData
  }

  function alterarMedico(index: number, nome: string) {
    const novasNotas = [...notas]

    novasNotas[index] = {
      ...novasNotas[index],
      Medico: nome,
    }

    setNotas(novasNotas)

    sessionStorage.setItem(
      'notas_faturamento',
      JSON.stringify(novasNotas)
    )
  }

  function calcularPcc(nota: Nota) {
    if (nota.SituacaoNota === 'C') {
      return 0
    }

    if (
      nota.ValorPccRetido !== undefined &&
      nota.ValorPccRetido !== null
    ) {
      return Number(nota.ValorPccRetido)
    }

    if ((nota.ValorCsll || 0) > 0) {
      return Number(
        ((nota.ValorTotal || 0) * 0.0465).toFixed(2)
      )
    }

    return 0
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
        'https://faturamento-medico-backend.onrender.com/faturamento/calcular',
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
        throw new Error('Erro ao calcular o faturamento.')
      }

      const resultado = await resposta.json()

      setCalculos(resultado)

      sessionStorage.setItem(
        'calculos_faturamento',
        JSON.stringify(resultado)
      )
    } catch (error) {
      console.error(error)
      setErroCalculo(
        'Não foi possível calcular o faturamento.'
      )
    } finally {
      setCalculando(false)
    }
  }

  function reiniciarFaturamento() {
    sessionStorage.removeItem('notas_faturamento')
    sessionStorage.removeItem('calculos_faturamento')
    sessionStorage.removeItem('honorario_total')
    sessionStorage.removeItem('darf_gps_total')
    sessionStorage.removeItem('honorario_por_medico')
    sessionStorage.removeItem('darf_gps_por_medico')

    setNotas([])
    setCalculos(null)
    setHonorarioTotal(0)
    setDarfGpsTotal(0)
    setErroCalculo('')
  }

  async function gerarExcel() {
    try {
      const resposta = await fetch(
        'https://faturamento-medico-backend.onrender.com/faturamento/excel',
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
        throw new Error('Erro ao gerar o Excel.')
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
      alert('Não foi possível gerar o Excel.')
    }
  }

  const faturamento =
    calculos?.totais?.total_faturamento || 0

  const ir =
    calculos?.totais?.total_ir || 0

  const pisCofinsCsll = notas.reduce(
    (total, nota) =>
      total + calcularPcc(nota),
    0
  )

  const valorLiq =
    faturamento -
    pisCofinsCsll -
    ir

  const protocolo =
    calculos?.protocolo || []

  return (
    <div className="min-h-screen bg-slate-50">
      <AppHeader />

      <main className="mx-auto max-w-7xl space-y-8 px-6 py-8">

        {/* CAMINHO */}
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

        {/* REINICIAR */}
        {notas.length > 0 && (
          <button
            type="button"
            onClick={reiniciarFaturamento}
            className="rounded-xl border border-red-200 bg-white px-4 py-2 text-sm font-semibold text-red-600 transition hover:bg-red-50"
          >
            🔄 Reiniciar
          </button>
        )}

        {/* UPLOAD */}
        <UploadPanel
          onNotasProcessadas={(dados) => {
            setNotas(dados)

            sessionStorage.setItem(
              'notas_faturamento',
              JSON.stringify(dados)
            )

            calcularFaturamento(
              dados,
              honorarioTotal,
              darfGpsTotal
            )
          }}
        />

        {/* ERRO */}
        {erroCalculo && (
          <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {erroCalculo}
          </div>
        )}

        {/* CALCULANDO */}
        {calculando && (
          <div className="rounded-xl border border-blue-200 bg-blue-50 px-4 py-3 text-sm text-blue-700">
            Calculando faturamento...
          </div>
        )}

        {notas.length > 0 && (
          <>

            {/* =============================== */}
            {/* NOTAS FISCAIS */}
            {/* =============================== */}

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

                <div className="max-h-[360px] overflow-auto">

                  <table className="min-w-[1150px] w-full text-left text-sm">

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
                          PCC-4,65%
                        </th>

                        <th className="whitespace-nowrap px-5 py-4 text-right font-semibold text-slate-600">
                          Valor Liq.
                        </th>

                        <th className="whitespace-nowrap px-5 py-4 font-semibold text-slate-600">
                          Médico
                        </th>

                      </tr>

                    </thead>

                    <tbody>

                      {notas.map((nota, index) => {

                        const cancelada =
                          String(nota.SituacaoNota || '')
                            .toUpperCase()
                            .trim() === 'C'

                        return (
                          <tr
                            key={index}
                            className={
                              cancelada
                                ? 'border-b border-red-200 bg-red-50 text-red-700 last:border-0'
                                : 'border-b border-slate-100 last:border-0 hover:bg-slate-50'
                            }
                          >

                            {/* DATA */}
                            <td className="whitespace-nowrap px-5 py-3 text-slate-600">
                              {formatarData(
                                nota.DataEmissao
                              )}
                            </td>

                            {/* CLIENTE */}
                            <td className="max-w-[240px] truncate px-5 py-3 text-slate-700">
                              {nota.TomadorServico || '-'}
                            </td>

                            {/* NF */}
                            <td className="whitespace-nowrap px-5 py-3 text-slate-600">
                              {nota.NumeroNF || '-'}
                            </td>

                            {/* VALOR */}
                            <td className="whitespace-nowrap px-5 py-3 text-right font-medium text-slate-800">
                              {formatarReais(
                                cancelada
                                  ? 0
                                  : nota.ValorTotal || 0
                              )}
                            </td>

                            {/* IR */}
                            <td className="whitespace-nowrap px-5 py-3 text-right text-slate-600">
                              {formatarReais(
                                cancelada
                                  ? 0
                                  : nota.ValorIr || 0
                              )}
                            </td>

                            {/* PCC */}
                            <td className="whitespace-nowrap px-5 py-3 text-right text-slate-600">
                              {formatarReais(
                                calcularPcc(nota)
                              )}
                            </td>

                            {/* VALOR LÍQUIDO */}
                            <td className="whitespace-nowrap px-5 py-3 text-right text-slate-600">
                              {formatarReais(
                                cancelada
                                  ? 0
                                  : (nota.ValorTotal || 0) -
                                      calcularPcc(nota) -
                                      (nota.ValorIr || 0)
                              )}
                            </td>

                            {/* MÉDICO EDITÁVEL */}
                            <td className="px-5 py-3">
                              <input
                                type="text"
                                value={nota.Medico || ''}
                                placeholder="Digite o médico"
                                disabled={cancelada}
                                onChange={(event) =>
                                  alterarMedico(index, event.target.value)
                                }
                                onBlur={(event) => {
                                  const novasNotas = [...notas]

                                  novasNotas[index] = {
                                    ...novasNotas[index],
                                    Medico: event.currentTarget.value,
                                  }

                                  setNotas(novasNotas)

                                  sessionStorage.setItem(
                                    'notas_faturamento',
                                    JSON.stringify(novasNotas)
                                  )

                                  calcularFaturamento(
                                    novasNotas,
                                    honorarioTotal,
                                    darfGpsTotal
                                  )
                                }}
                                onKeyDown={(event) => {
                                  if (event.key === 'Enter') {
                                    event.currentTarget.blur()
                                  }
                                }}
                                className={
                                  cancelada
                                    ? 'w-[230px] rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-400 outline-none'
                                    : 'w-[230px] rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm font-medium text-slate-700 outline-none transition placeholder:text-slate-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-100'
                                }
                              />
                            </td>

                          </tr>
                        )
                      })}

                    </tbody>

                  </table>

                </div>

                <div className="flex items-center justify-between border-t border-slate-100 bg-slate-50 px-5 py-3">

                  <span className="text-xs text-slate-500">
                    {notas.length} registro(s)
                  </span>

                  <span className="text-xs text-slate-400">
                    Digite o médico diretamente na tabela
                  </span>

                </div>

              </div>

            </section>


            {/* =============================== */}
            {/* VALORES TOTAIS */}
            {/* =============================== */}

            <section>

              <h2 className="mb-4 text-xl font-semibold text-slate-900">
                Valores Totais
              </h2>

              <div className="grid gap-4 md:grid-cols-4">

                <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
                  <p className="text-sm text-slate-500">
                    Faturamento
                  </p>

                  <p className="mt-2 text-2xl font-bold text-slate-900">
                    {formatarReais(faturamento)}
                  </p>
                </div>

                <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
                  <p className="text-sm text-slate-500">
                    IR
                  </p>

                  <p className="mt-2 text-2xl font-bold text-slate-900">
                    {formatarReais(ir)}
                  </p>
                </div>

                <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
                  <p className="text-sm text-slate-500">
                    PCC - 4,65%
                  </p>

                  <p className="mt-2 text-2xl font-bold text-slate-900">
                    {formatarReais(pisCofinsCsll)}
                  </p>
                </div>

                <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
                  <p className="text-sm text-slate-500">
                    Valor Líquido
                  </p>

                  <p className="mt-2 text-2xl font-bold text-slate-900">
                    {formatarReais(valorLiq)}
                  </p>
                </div>

              </div>

            </section>


            {/* =============================== */}
            {/* VALORES PARA CÁLCULO */}
            {/* =============================== */}

            <section>

              <h2 className="mb-4 text-xl font-semibold text-slate-900">
                Valores para cálculo
              </h2>

              <div className="grid gap-6 md:grid-cols-2">

                <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">

                  <label className="block text-sm font-semibold text-slate-700">
                    Honorário total
                  </label>

                  <input
                    type="number"
                    step="0.01"
                    value={honorarioTotal}
                    onChange={(event) => {
                      const valor =
                        Number(event.target.value) || 0

                      setHonorarioTotal(valor)

                      sessionStorage.setItem(
                        'honorario_total',
                        String(valor)
                      )

                      calcularFaturamento(
                        notas,
                        valor,
                        darfGpsTotal
                      )
                    }}
                    className="mt-2 w-full rounded-xl border border-slate-300 px-4 py-3 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                  />

                </div>


                <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">

                  <label className="block text-sm font-semibold text-slate-700">
                    DARF / GPS total
                  </label>

                  <input
                    type="number"
                    step="0.01"
                    value={darfGpsTotal}
                    onChange={(event) => {

                      const valor =
                        Number(event.target.value) || 0

                      setDarfGpsTotal(valor)

                      sessionStorage.setItem(
                        'darf_gps_total',
                        String(valor)
                      )

                      calcularFaturamento(
                        notas,
                        honorarioTotal,
                        valor
                      )
                    }}
                    className="mt-2 w-full rounded-xl border border-slate-300 px-4 py-3 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                  />

                </div>

              </div>

            </section>


            {/* =============================== */}
            {/* PROTOCOLO */}
            {/* =============================== */}

            {protocolo.length > 0 && (

              <section>

                <div className="mb-4">
                  <h2 className="text-xl font-semibold text-slate-900">
                    Protocolo de Impostos
                  </h2>

                  <p className="mt-1 text-sm text-slate-500">
                    Resumo dos impostos calculados.
                  </p>
                </div>

                <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">

                  <div className="overflow-x-auto">

                    <table className="w-full text-left text-sm">

                      <thead className="bg-slate-100">

                        <tr className="border-b border-slate-200">

                          <th className="px-5 py-4 font-semibold text-slate-600">
                            DESCRIÇÃO
                          </th>

                          <th className="px-5 py-4 font-semibold text-slate-600">
                            VENCIMENTO
                          </th>

                          <th className="px-5 py-4 text-right font-semibold text-slate-600">
                            CALCULADO
                          </th>

                          <th className="px-5 py-4 text-right font-semibold text-slate-600">
                            RETIDO
                          </th>

                          <th className="px-5 py-4 text-right font-semibold text-slate-600">
                            A PAGAR
                          </th>

                        </tr>

                      </thead>

                      <tbody>

                        {protocolo
                          .filter(
                            (item: any) =>
                              item['Descrição'] !== 'TOTAL'
                          )
                          .map(
                            (item: any, index: number) => (

                              <tr
                                key={index}
                                className="border-b border-slate-100 last:border-0"
                              >

                                <td className="px-5 py-3 font-medium text-slate-700">
                                  {item['Descrição']}
                                </td>

                                <td className="px-5 py-3 text-slate-600">
                                  {item['Vencimento'] || '-'}
                                </td>

                                <td className="px-5 py-3 text-right text-slate-700">
                                  {formatarReais(
                                    Number(
                                      item['Calculado'] || 0
                                    )
                                  )}
                                </td>

                                <td className="px-5 py-3 text-right text-slate-700">
                                  {formatarReais(
                                    Number(
                                      item['Retido'] || 0
                                    )
                                  )}
                                </td>

                                <td className="px-5 py-3 text-right font-semibold text-slate-900">
                                  {formatarReais(
                                    Number(
                                      item['A pagar'] || 0
                                    )
                                  )}
                                </td>

                              </tr>

                            )
                          )}

                      </tbody>

                    </table>

                  </div>


                  <div className="flex items-center justify-between border-t border-slate-200 bg-slate-50 px-5 py-4">

                    <span className="font-semibold text-slate-700">
                      TOTAL
                    </span>

                    <span className="text-lg font-bold text-slate-900">

                      {formatarReais(
                        Number(
                          protocolo.find(
                            (item: any) =>
                              item['Descrição'] === 'TOTAL'
                          )?.['A pagar'] || 0
                        )
                      )}

                    </span>

                  </div>

                </div>

              </section>

            )}


            {/* =============================== */}
            {/* DEMONSTRATIVO */}
            {/* =============================== */}

            {calculos?.demonstrativo &&
              calculos.demonstrativo.length > 0 && (

                <section>

                  <div className="mb-4 flex items-center justify-between">

                    <div>
                      <h2 className="text-xl font-semibold text-slate-900">
                        Demonstrativo por Médico
                      </h2>

                      <p className="mt-1 text-sm text-slate-500">
                        Valores separados por médico.
                      </p>
                    </div>


                  </div>


                  <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">

                    <div className="overflow-x-auto">

                      <table className="w-full text-left text-sm">

                        <thead className="bg-slate-100">

                          <tr className="border-b border-slate-200">

                            <th className="px-5 py-4 font-semibold text-slate-600">
                              Médico
                            </th>

                            <th className="px-5 py-4 text-right font-semibold text-slate-600">
                              Valor dos Impostos
                            </th>

                          </tr>

                        </thead>

                        <tbody>

                          {calculos.demonstrativo.map(
                            (linha: any, index: number) => {

                              const medico =
                                linha['Médico']

                              const total =
                                linha['Valor dos Impostos']

                              return (
                                <tr
                                  key={index}
                                  className={
                                    medico === 'TOTAL'
                                      ? 'border-t border-slate-200 bg-slate-50'
                                      : 'border-b border-slate-100'
                                  }
                                >

                                  <td
                                    className={
                                      medico === 'TOTAL'
                                        ? 'px-5 py-4 font-bold text-slate-900'
                                        : 'px-5 py-4 font-medium text-slate-700'
                                    }
                                  >
                                    {medico === 'TOTAL' ? (
                                      medico
                                    ) : (
                                      <button
                                        type="button"
                                        onClick={() => {
                                          navigate({
                                            to: '/medico',
                                            search: {
                                              medico: medico,
                                              dados: '',
                                            },
                                          })
                                        }}
                                        className="text-left font-medium text-blue-600 hover:underline"
                                      >
                                        {medico || '-'}
                                      </button>
                                    )}
                                  </td>

                                  <td
                                    className={
                                      medico === 'TOTAL'
                                        ? 'px-5 py-4 text-right font-bold text-slate-900'
                                        : 'px-5 py-4 text-right font-semibold text-slate-800'
                                    }
                                  >
                                    {formatarReais(
                                      Number(total || 0)
                                    )}
                                  </td>

                                </tr>
                              )
                            }
                          )}

                        </tbody>

                      </table>

                    </div>

                  </div>

                </section>
              )}


            {/* =============================== */}
            {/* EXCEL */}
            {/* =============================== */}

            <section className="flex justify-end">

              <button
                type="button"
                onClick={gerarExcel}
                className="rounded-xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white transition hover:bg-slate-800"
              >
                📊 Gerar Excel
              </button>

            </section>


            {/* =============================== */}
            {/* DATA DE ENVIO */}
            {/* =============================== */}

            <section>

              <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">

                <label className="block text-sm font-semibold text-slate-700">
                  Data de envio
                </label>

                <input
                  type="date"
                  className="mt-2 rounded-xl border border-slate-300 px-4 py-3 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                />

              </div>

            </section>

          </>
        )}

        {/* =============================== */}
        {/* SEM NOTAS */}
        {/* =============================== */}

        {notas.length === 0 && (
          <div className="rounded-2xl border border-dashed border-slate-300 bg-white px-6 py-12 text-center">

            <h2 className="text-lg font-semibold text-slate-700">
              Nenhuma nota carregada
            </h2>

            <p className="mt-2 text-sm text-slate-500">
              Envie os arquivos para começar o cálculo do faturamento.
            </p>

          </div>
        )}

      </main>
    </div>
  )
}