// ============================================================
// ORDENAÇÃO DA TABELA DE NOTAS FISCAIS
//
// - Datas: aceita 30/10/2026 13:55:17 (São Paulo) e
//   2026-10-30T16:08:02 (Ginfes / GISS) e ordena como data.
// - Valores e número da NF: ordenados como número.
// - Textos: ordenados em português (acentos não atrapalham).
// - Campos vazios ficam sempre no final.
// ============================================================

export type ColunaNota =
  | 'data'
  | 'cliente'
  | 'nf'
  | 'valor'
  | 'ir'
  | 'pcc'
  | 'liquido'
  | 'medico'

export type Direcao = 'asc' | 'desc'

export type NotaOrdenavel = {
  DataEmissao?: string
  TomadorServico?: string
  NumeroNF?: string
  ValorTotal?: number
  ValorIr?: number
  SituacaoNota?: string
  Medico?: string
}

export function converterData(texto?: string): number | null {
  if (!texto) return null

  const t = texto.trim()

  // Padrão brasileiro: dd/mm/aaaa [hh:mm[:ss]]
  let m = t.match(
    /^(\d{2})\/(\d{2})\/(\d{4})(?:[ T](\d{2}):(\d{2})(?::(\d{2}))?)?/
  )

  if (m) {
    return new Date(
      Number(m[3]),
      Number(m[2]) - 1,
      Number(m[1]),
      Number(m[4] || 0),
      Number(m[5] || 0),
      Number(m[6] || 0)
    ).getTime()
  }

  // ISO: aaaa-mm-dd[Thh:mm[:ss[.fff]]][fuso]
  m = t.match(
    /^(\d{4})-(\d{2})-(\d{2})(?:[T ](\d{2}):(\d{2})(?::(\d{2}))?)?/
  )

  if (m) {
    return new Date(
      Number(m[1]),
      Number(m[2]) - 1,
      Number(m[3]),
      Number(m[4] || 0),
      Number(m[5] || 0),
      Number(m[6] || 0)
    ).getTime()
  }

  return null
}

function numeroDaNota(nota: NotaOrdenavel): number | null {
  const digitos = String(nota.NumeroNF || '').replace(/\D/g, '')
  return digitos ? Number(digitos) : null
}

function valorDaColuna(
  nota: NotaOrdenavel,
  coluna: ColunaNota,
  calcularPcc: (nota: NotaOrdenavel) => number
): number | string | null {
  const cancelada =
    String(nota.SituacaoNota || '').toUpperCase().trim() === 'C'

  switch (coluna) {
    case 'data':
      return converterData(nota.DataEmissao)

    case 'cliente':
      return (nota.TomadorServico || '').trim() || null

    case 'nf':
      return numeroDaNota(nota)

    // Os valores seguem o que a tabela mostra (cancelada = 0)
    case 'valor':
      return cancelada ? 0 : nota.ValorTotal || 0

    case 'ir':
      return cancelada ? 0 : nota.ValorIr || 0

    case 'pcc':
      return calcularPcc(nota)

    case 'liquido':
      return cancelada
        ? 0
        : (nota.ValorTotal || 0) - calcularPcc(nota) - (nota.ValorIr || 0)

    case 'medico':
      return (nota.Medico || '').trim() || null
  }
}

function comparar(
  a: number | string | null,
  b: number | string | null
): number {
  if (typeof a === 'number' && typeof b === 'number') return a - b

  return String(a).localeCompare(String(b), 'pt-BR', {
    sensitivity: 'base',
    numeric: true,
  })
}

/**
 * Devolve a lista de POSIÇÕES das notas na ordem pedida.
 * (posições, e não cópias das notas, para a edição do médico
 * continuar apontando para a nota certa)
 */
export function ordenarIndices(
  notas: NotaOrdenavel[],
  coluna: ColunaNota,
  direcao: Direcao,
  calcularPcc: (nota: NotaOrdenavel) => number
): number[] {
  const sinal = direcao === 'asc' ? 1 : -1

  const itens = notas.map((nota, indice) => ({
    indice,
    chave: valorDaColuna(nota, coluna, calcularPcc),
    nf: numeroDaNota(nota),
  }))

  itens.sort((x, y) => {
    // vazios sempre no final, nos dois sentidos
    if (x.chave === null && y.chave !== null) return 1
    if (x.chave !== null && y.chave === null) return -1

    if (x.chave !== null && y.chave !== null) {
      const diferenca = comparar(x.chave, y.chave)
      if (diferenca !== 0) return diferenca * sinal
    }

    // empate: número da nota, depois posição original
    if (x.nf !== null && y.nf !== null && x.nf !== y.nf) {
      return (x.nf - y.nf) * sinal
    }

    return x.indice - y.indice
  })

  return itens.map((item) => item.indice)
}