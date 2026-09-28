import { useEffect, useState } from 'react'
import {
  createFileRoute,
  useNavigate,
} from '@tanstack/react-router'

type Nota = {
  Prestador?: string
  DataEmissao?: string
  NumeroNF?: string
  TomadorServico?: string
  ValorTotal?: number
  ValorIr?: number
  ValorInss?: number
  ValorIss?: number
  ValorCsll?: number
  ValorPisRetido?: number
  ValorCofinsRetido?: number
  ValorCsllRetido?: number
  ValorPccRetido?: number
  SituacaoNota?: string
  TotalImpostos?: number
  Medico?: string
}

type DetalheMedico = {
  medico?: string
  faturamento?: number
  iss?: number
  inss?: number
  ir_destacado?: number
  pcc_retido?: number
  base_pcc?: number

  pis_calculado?: number
  pis_retido_pcc?: number
  pis_a_pagar?: number

  cofins_calculado?: number
  cofins_retido_pcc?: number
  cofins_a_pagar?: number

  csll_calculado?: number
  csll_retido_pcc?: number
  csll_a_pagar?: number

  ir_calculado?: number
  ir_a_pagar?: number

  honorario?: number
  darf_gps?: number

  total_liquido?: number
  total_impostos?: number
}

export const Route = createFileRoute('/medico')({
  validateSearch: (search) => ({
    medico: String(search.medico || ''),
    dados: String(search.dados || ''),
  }),
  component: MedicoPage,
})

function formatarReais(valor: number) {
  return `R$ ${Number(valor || 0).toLocaleString('pt-BR', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`
}

function formatarData(data?: string) {
  if (!data) return ''

  const dataParte = data.split('T')[0].split(' ')[0]
  const partes = dataParte.split('-')

  if (partes.length === 3) {
    return `${partes[2]}/${partes[1]}/${partes[0]}`
  }

  return dataParte
}

function MedicoPage() {
  const navigate = useNavigate()

  const { medico } = Route.useSearch()

  const [notas, setNotas] = useState<Nota[]>([])
  const [detalheMedico, setDetalheMedico] =
    useState<DetalheMedico | null>(null)

  /*
   * ============================================================
   * CARREGAR NOTAS
   * ============================================================
   */

  useEffect(() => {
    const dadosSalvos = sessionStorage.getItem(
      'notas_faturamento'
    )

    if (!dadosSalvos) {
      return
    }

    try {
      const dados: Nota[] = JSON.parse(dadosSalvos)

      const notasDoMedico = dados.filter(
        (nota) =>
          nota.Medico === medico &&
          String(nota.SituacaoNota || '')
            .toUpperCase()
            .trim() !== 'C'
      )

      setNotas(notasDoMedico)
    } catch (error) {
      console.error(
        'Erro ao carregar notas:',
        error
      )
    }
  }, [medico])

  /*
   * ============================================================
   * CARREGAR CÁLCULOS FEITOS PELO PYTHON
   *
   * O medico.tsx NÃO recalcula impostos.
   * Ele somente lê calculos_faturamento.
   * ============================================================
   */

  useEffect(() => {
    const calculosSalvos = sessionStorage.getItem(
      'calculos_faturamento'
    )

    if (!calculosSalvos) {
      return
    }

    try {
      const calculos = JSON.parse(
        calculosSalvos
      )

      const detalhes: DetalheMedico[] =
        calculos?.detalhes_medicos || []

      const encontrado = detalhes.find(
        (item) =>
          String(item.medico || '').trim() ===
          String(medico || '').trim()
      )

      setDetalheMedico(
        encontrado || null
      )
    } catch (error) {
      console.error(
        'Erro ao carregar cálculos:',
        error
      )
    }
  }, [medico])

  /*
   * ============================================================
   * VALORES VINDOS DO PYTHON
   * ============================================================
   */

  const faturamento =
    Number(
      detalheMedico?.faturamento || 0
    )

  const issDestacado =
    Number(
      detalheMedico?.iss || 0
    )

  const inssDestacado =
    Number(
      detalheMedico?.inss || 0
    )

  const irDestacado =
    Number(
      detalheMedico?.ir_destacado || 0
    )

  const pccRetido =
    Number(
      detalheMedico?.pcc_retido || 0
    )

  const totalLiquido =
    Number(
      detalheMedico?.total_liquido || 0
    )

  /*
   * ============================================================
   * IMPOSTOS
   *
   * TODOS ESTES VALORES JÁ FORAM CALCULADOS
   * PELO calculos.py
   * ============================================================
   */

  const cofinsCalculado =
    Number(
      detalheMedico?.cofins_calculado || 0
    )

  const cofinsRetidoPcc =
    Number(
      detalheMedico?.cofins_retido_pcc || 0
    )

  const cofinsAPagar =
    Number(
      detalheMedico?.cofins_a_pagar || 0
    )

  const pisCalculado =
    Number(
      detalheMedico?.pis_calculado || 0
    )

  const pisRetidoPcc =
    Number(
      detalheMedico?.pis_retido_pcc || 0
    )

  const pisAPagar =
    Number(
      detalheMedico?.pis_a_pagar || 0
    )

  const csllCalculado =
    Number(
      detalheMedico?.csll_calculado || 0
    )

  const csllRetidoPcc =
    Number(
      detalheMedico?.csll_retido_pcc || 0
    )

  const csllAPagar =
    Number(
      detalheMedico?.csll_a_pagar || 0
    )

  const irCalculado =
    Number(
      detalheMedico?.ir_calculado || 0
    )

  const irAPagar =
    Number(
      detalheMedico?.ir_a_pagar || 0
    )

  /*
   * ============================================================
   * RESUMO
   *
   * Também vêm diretamente do calculos.py
   * ============================================================
   */

  const honorarioPorMedico =
    Number(
      detalheMedico?.honorario || 0
    )

  const darfGpsPorMedico =
    Number(
      detalheMedico?.darf_gps || 0
    )

  const totalImpostos =
    Number(
      detalheMedico?.total_impostos || 0
    )

  return (
    <main className="min-h-screen bg-slate-50">
      {/* ======================================================
          CABEÇALHO
      ====================================================== */}
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-5">
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-slate-900">
              🏥 Faturamento Médico
            </h1>

            <p className="mt-1 text-sm text-slate-500">
              Gestão de faturamento, notas fiscais e impostos
            </p>
          </div>

          <div className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-2">
            <span className="text-sm font-medium text-slate-600">
              Sistema
            </span>

            <span className="ml-2 text-sm font-semibold text-emerald-600">
              ● Online
            </span>
          </div>
        </div>
      </header>

      {/* ======================================================
          CONTEÚDO
      ====================================================== */}

      <div className="mx-auto max-w-7xl px-6 py-8">

        {/* VOLTAR */}

        <button
          type="button"
          onClick={() =>
            navigate({
              to: '/',
            })
          }
          className="mb-6 rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-700 shadow-sm transition hover:bg-slate-50"
        >
          ← Voltar
        </button>

        {/* TÍTULO */}

        <div className="mb-8">
          <p className="text-sm font-medium text-blue-700">
            Demonstrativo de impostos
          </p>

          <h2 className="mt-1 text-3xl font-bold tracking-tight text-slate-900">
            {medico || 'Médico'}
          </h2>

          <p className="mt-2 text-sm text-slate-500">
            FATURAMENTO - AGOSTO - 2026
          </p>
        </div>

        {/* ====================================================
            FATURAMENTO
        ==================================================== */}

        <section className="rounded-2xl border border-slate-200 bg-white shadow-sm">

          <div className="border-b border-slate-100 px-6 py-5">
            <h3 className="text-base font-semibold text-slate-900">
              Faturamento
            </h3>

            <p className="mt-1 text-sm text-slate-500">
              Notas fiscais vinculadas ao médico.
            </p>
          </div>

          <div className="max-h-[300px] overflow-y-auto overflow-x-auto">

            <table className="w-full text-sm">

              <thead className="bg-slate-50">

                <tr className="sticky top-0 z-10 border-b border-slate-200 bg-white">

                  <th className="px-6 py-4 text-left font-semibold text-slate-600">
                    DATA
                  </th>

                  <th className="px-6 py-4 text-left font-semibold text-slate-600">
                    CLIENTE
                  </th>

                  <th className="px-6 py-4 text-left font-semibold text-slate-600">
                    N.FISCAL
                  </th>

                  <th className="px-6 py-4 text-right font-semibold text-slate-600">
                    VALOR
                  </th>

                  <th className="px-6 py-4 text-right font-semibold text-slate-600">
                    IR
                  </th>

                  <th className="px-6 py-4 text-right font-semibold text-slate-600">
                    PCC
                  </th>

                  <th className="px-6 py-4 text-right font-semibold text-slate-600">
                    TAXA ADM
                  </th>

                  <th className="px-6 py-4 text-right font-semibold text-slate-600">
                    VALOR LÍQ.
                  </th>

                </tr>

              </thead>

              <tbody>

                {notas.length === 0 ? (

                  <tr>

                    <td
                      colSpan={8}
                      className="px-6 py-10 text-center text-sm text-slate-500"
                    >
                      Nenhuma nota encontrada para este médico.
                    </td>

                  </tr>

                ) : (

                  notas.map((nota, index) => {

                    const valor =
                      Number(
                        nota.ValorTotal || 0
                      )

                    const ir =
                      Number(
                        nota.ValorIr || 0
                      )

                    const pcc =
                      Number(
                        nota.ValorPccRetido || 0
                      )

                    const inss =
                      Number(
                        nota.ValorInss || 0
                      )

                    /*
                     * O valor líquido por nota ainda utiliza
                     * o valor que veio da nota.
                     *
                     * Regra:
                     * VALOR - IR - PCC
                     */

                    const liquido =
                      valor -
                      ir -
                      pcc

                    return (

                      <tr
                        key={index}
                        className="border-b border-slate-100"
                      >

                        <td className="px-6 py-4 text-slate-600">
                          {formatarData(
                            nota.DataEmissao
                          )}
                        </td>

                        <td className="px-6 py-4 font-medium text-slate-700">
                          {nota.TomadorServico || '-'}
                        </td>

                        <td className="px-6 py-4 text-slate-600">
                          {nota.NumeroNF || '-'}
                        </td>

                        <td className="px-6 py-4 text-right font-semibold text-slate-800">
                          {formatarReais(valor)}
                        </td>

                        <td className="px-6 py-4 text-right text-slate-600">
                          {formatarReais(ir)}
                        </td>

                        <td className="px-6 py-4 text-right text-slate-600">
                          {formatarReais(pcc)}
                        </td>

                        <td className="px-6 py-4 text-right text-slate-600">
                          {formatarReais(inss)}
                        </td>

                        <td className="px-6 py-4 text-right font-semibold text-slate-800">
                          {formatarReais(liquido)}
                        </td>

                      </tr>

                    )
                  })

                )}

              </tbody>

            </table>

          </div>

          {/* TOTAL */}

          <div className="grid gap-4 border-t border-slate-100 bg-slate-50 p-6 md:grid-cols-6">

            <div>
              <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                Faturamento
              </p>

              <p className="mt-1 text-lg font-bold text-slate-900">
                {formatarReais(faturamento)}
              </p>
            </div>

            <div>
              <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                ISS
              </p>

              <p className="mt-1 text-lg font-bold text-slate-900">
                {formatarReais(issDestacado)}
              </p>
            </div>

            <div>
              <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                INSS
              </p>

              <p className="mt-1 text-lg font-bold text-slate-900">
                {formatarReais(inssDestacado)}
              </p>
            </div>

            <div>
              <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                IR
              </p>

              <p className="mt-1 text-lg font-bold text-slate-900">
                {formatarReais(irDestacado)}
              </p>
            </div>

            <div>
              <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                PCC
              </p>

              <p className="mt-1 text-lg font-bold text-slate-900">
                {formatarReais(pccRetido)}
              </p>
            </div>

            <div>
              <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                TOTAL LIQ
              </p>

              <p className="mt-1 text-lg font-bold text-slate-900">
                {formatarReais(totalLiquido)}
              </p>
            </div>

          </div>

        </section>

        {/* ====================================================
            IMPOSTOS
        ==================================================== */}

        <section className="mt-8 rounded-2xl border border-slate-200 bg-white shadow-sm">

          <div className="border-b border-slate-100 px-6 py-5">

            <h3 className="text-base font-semibold text-slate-900">
              Demonstrativo de Impostos
            </h3>

            <p className="mt-1 text-sm text-slate-500">
              Cálculo dos impostos e valores já destacados nas notas fiscais.
            </p>

          </div>

          <div className="max-h-[350px] overflow-y-auto overflow-x-auto">

            <table className="w-full text-sm">

              <thead className="bg-slate-50">

                <tr className="border-b border-slate-200">

                  <th className="px-6 py-4 text-left font-semibold text-slate-600">
                    IMPOSTO
                  </th>

                  <th className="px-6 py-4 text-right font-semibold text-slate-600">
                    BASE
                  </th>

                  <th className="px-6 py-4 text-right font-semibold text-slate-600">
                    ALÍQUOTA
                  </th>

                  <th className="px-6 py-4 text-right font-semibold text-slate-600">
                    CALCULADO
                  </th>

                  <th className="px-6 py-4 text-right font-semibold text-slate-600">
                    RETIDO NF
                  </th>

                  <th className="px-6 py-4 text-right font-semibold text-slate-600">
                    A PAGAR
                  </th>

                </tr>

              </thead>

              <tbody>

                {/* ISS */}

                <tr className="border-b border-slate-100">

                  <td className="px-6 py-4 font-medium text-slate-700">
                    ISS
                  </td>

                  <td className="px-6 py-4 text-right text-slate-600">
                    {formatarReais(faturamento)}
                  </td>

                  <td className="px-6 py-4 text-right text-slate-600">
                    —
                  </td>

                  <td className="px-6 py-4 text-right text-slate-800">
                    {formatarReais(issDestacado)}
                  </td>

                  <td className="px-6 py-4 text-right text-slate-600">
                    {formatarReais(issDestacado)}
                  </td>

                  <td className="px-6 py-4 text-right font-semibold text-slate-800">
                    {formatarReais(issDestacado)}
                  </td>

                </tr>

                {/* COFINS */}

                <tr className="border-b border-slate-100">

                  <td className="px-6 py-4 font-medium text-slate-700">
                    COFINS
                  </td>

                  <td className="px-6 py-4 text-right text-slate-600">
                    {formatarReais(faturamento)}
                  </td>

                  <td className="px-6 py-4 text-right text-slate-600">
                    3,00%
                  </td>

                  <td className="px-6 py-4 text-right text-slate-800">
                    {formatarReais(cofinsCalculado)}
                  </td>

                  <td className="px-6 py-4 text-right text-slate-600">
                    {formatarReais(cofinsRetidoPcc)}
                  </td>

                  <td className="px-6 py-4 text-right font-semibold text-slate-800">
                    {formatarReais(cofinsAPagar)}
                  </td>

                </tr>

                {/* PIS */}

                <tr className="border-b border-slate-100">

                  <td className="px-6 py-4 font-medium text-slate-700">
                    PIS
                  </td>

                  <td className="px-6 py-4 text-right text-slate-600">
                    {formatarReais(faturamento)}
                  </td>

                  <td className="px-6 py-4 text-right text-slate-600">
                    0,65%
                  </td>

                  <td className="px-6 py-4 text-right text-slate-800">
                    {formatarReais(pisCalculado)}
                  </td>

                  <td className="px-6 py-4 text-right text-slate-600">
                    {formatarReais(pisRetidoPcc)}
                  </td>

                  <td className="px-6 py-4 text-right font-semibold text-slate-800">
                    {formatarReais(pisAPagar)}
                  </td>

                </tr>

                {/* CSLL */}

                <tr className="border-b border-slate-100">

                  <td className="px-6 py-4 font-medium text-slate-700">
                    CSLL
                  </td>

                  <td className="px-6 py-4 text-right text-slate-600">
                    {formatarReais(faturamento)}
                  </td>

                  <td className="px-6 py-4 text-right text-slate-600">
                    1,08%
                  </td>

                  <td className="px-6 py-4 text-right text-slate-800">
                    {formatarReais(csllCalculado)}
                  </td>

                  <td className="px-6 py-4 text-right text-slate-600">
                    {formatarReais(csllRetidoPcc)}
                  </td>

                  <td className="px-6 py-4 text-right font-semibold text-slate-800">
                    {formatarReais(csllAPagar)}
                  </td>

                </tr>

                {/* IRPJ */}

                <tr className="border-b border-slate-100">

                  <td className="px-6 py-4 font-medium text-slate-700">
                    IRPJ
                  </td>

                  <td className="px-6 py-4 text-right text-slate-600">
                    {formatarReais(faturamento)}
                  </td>

                  <td className="px-6 py-4 text-right text-slate-600">
                    1,20%
                  </td>

                  <td className="px-6 py-4 text-right text-slate-800">
                    {formatarReais(irCalculado)}
                  </td>

                  <td className="px-6 py-4 text-right text-slate-600">
                    {formatarReais(irDestacado)}
                  </td>

                  <td className="px-6 py-4 text-right font-semibold text-slate-800">
                    {formatarReais(irAPagar)}
                  </td>

                </tr>

              </tbody>

            </table>

          </div>

          {/* TOTAL DOS IMPOSTOS DESTACADOS */}

          <div className="grid gap-4 border-t border-slate-100 bg-slate-50 p-6 md:grid-cols-3">

            <div>

              <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                PCC RETIDO
              </p>

              <p className="mt-1 text-lg font-bold text-slate-900">
                {formatarReais(pccRetido)}
              </p>

            </div>

            <div>

              <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                Total líquido das notas
              </p>

              <p className="mt-1 text-lg font-bold text-slate-900">
                {formatarReais(totalLiquido)}
              </p>

            </div>

            <div>

              <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                Total dos impostos
              </p>

              <p className="mt-1 text-xl font-bold text-blue-900">
                {formatarReais(totalImpostos)}
              </p>

            </div>

          </div>

        </section>

        {/* ====================================================
            RESUMO PARA PAGAMENTO
        ==================================================== */}

        <section className="mt-8 rounded-2xl border border-slate-200 bg-white shadow-sm">

          <div className="border-b border-slate-100 px-6 py-5">

            <h3 className="text-base font-semibold text-slate-900">
              Resumo para pagamento
            </h3>

            <p className="mt-1 text-sm text-slate-500">
              Composição do valor final por médico.
            </p>

          </div>

          <div className="overflow-x-auto">

            <table className="w-full text-sm">

              <thead className="bg-slate-50">

                <tr className="border-b border-slate-200">

                  <th className="px-6 py-4 text-left font-semibold text-slate-600">
                    DESCRIÇÃO
                  </th>

                  <th className="px-6 py-4 text-right font-semibold text-slate-600">
                    VALOR
                  </th>

                </tr>

              </thead>

              <tbody>

                <tr className="border-b border-slate-100">

                  <td className="px-6 py-4 text-slate-700">
                    Honorário
                  </td>

                  <td className="px-6 py-4 text-right font-semibold text-slate-800">
                    {formatarReais(honorarioPorMedico)}
                  </td>

                </tr>

                <tr className="border-b border-slate-100">

                  <td className="px-6 py-4 text-slate-700">
                    ISS
                  </td>

                  <td className="px-6 py-4 text-right font-semibold text-slate-800">
                    {formatarReais(issDestacado)}
                  </td>

                </tr>

                <tr className="border-b border-slate-100">

                  <td className="px-6 py-4 text-slate-700">
                    DARF / GPS
                  </td>

                  <td className="px-6 py-4 text-right font-semibold text-slate-800">
                    {formatarReais(darfGpsPorMedico)}
                  </td>

                </tr>

                <tr className="border-b border-slate-100">

                  <td className="px-6 py-4 text-slate-700">
                    COFINS a pagar
                  </td>

                  <td className="px-6 py-4 text-right font-semibold text-slate-800">
                    {formatarReais(cofinsAPagar)}
                  </td>

                </tr>

                <tr className="border-b border-slate-100">

                  <td className="px-6 py-4 text-slate-700">
                    PIS a pagar
                  </td>

                  <td className="px-6 py-4 text-right font-semibold text-slate-800">
                    {formatarReais(pisAPagar)}
                  </td>

                </tr>

                <tr className="border-b border-slate-100">

                  <td className="px-6 py-4 text-slate-700">
                    CSLL a pagar
                  </td>

                  <td className="px-6 py-4 text-right font-semibold text-slate-800">
                    {formatarReais(csllAPagar)}
                  </td>

                </tr>

                <tr className="border-b border-slate-100">

                  <td className="px-6 py-4 text-slate-700">
                    IRPJ a pagar
                  </td>

                  <td className="px-6 py-4 text-right font-semibold text-slate-800">
                    {formatarReais(irAPagar)}
                  </td>

                </tr>

              </tbody>

              <tfoot>

                <tr className="bg-blue-50">

                  <td className="px-6 py-5 text-base font-bold text-slate-900">
                    TOTAL
                  </td>

                  <td className="px-6 py-5 text-right text-xl font-bold text-blue-900">
                    {formatarReais(totalImpostos)}
                  </td>

                </tr>

              </tfoot>

            </table>

          </div>

        </section>

      </div>

    </main>
  )
}