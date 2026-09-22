import { useState } from 'react'

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

type UploadPanelProps = {
  onNotasProcessadas: (notas: Nota[]) => void
}

export function UploadPanel({
  onNotasProcessadas,
}: UploadPanelProps) {

  const [arquivos, setArquivos] = useState<FileList | null>(null)
  const [carregando, setCarregando] = useState(false)
  const [erro, setErro] = useState('')

  async function processarArquivos() {

    if (!arquivos || arquivos.length === 0) {
      setErro('Selecione pelo menos um arquivo XML.')
      return
    }

    setErro('')
    setCarregando(true)

    try {

      const formData = new FormData()

      for (const arquivo of Array.from(arquivos)) {
        formData.append('arquivos', arquivo)
      }

      const resposta = await fetch(
        'http://127.0.0.1:8000/notas/processar',
        {
          method: 'POST',
          body: formData,
        }
      )

      if (!resposta.ok) {
        throw new Error('Erro ao processar os arquivos XML.')
      }

      const resultado = await resposta.json()

      onNotasProcessadas(resultado.dados)

    } catch (error) {

      console.error(error)

      setErro(
        'Não foi possível processar os arquivos XML.'
      )

    } finally {

      setCarregando(false)

    }
  }

  return (
    <section className="rounded-2xl border border-slate-200 bg-white shadow-sm">

      {/* CABEÇALHO DO PAINEL */}

      <div className="border-b border-slate-100 px-6 py-5">

        <div className="flex items-center gap-3">

          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-50 text-xl">
            📄
          </div>

          <div>

            <h2 className="text-base font-semibold text-slate-900">
              Importar notas fiscais
            </h2>

            <p className="text-sm text-slate-500">
              Adicione os arquivos XML para iniciar o processamento.
            </p>

          </div>

        </div>

      </div>


      {/* ÁREA DE UPLOAD */}

      <div className="p-6">

        <label
          htmlFor="xml-upload"
          className="group flex cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed border-slate-300 bg-slate-50 px-6 py-12 text-center transition hover:border-blue-400 hover:bg-blue-50/40"
        >

          <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-white text-3xl shadow-sm">
            📁
          </div>

          <h3 className="mt-5 text-base font-semibold text-slate-800">
            Selecione seus arquivos XML
          </h3>

          <p className="mt-2 max-w-md text-sm text-slate-500">
            Você pode selecionar vários arquivos de notas fiscais
            para processar de uma só vez.
          </p>

          <span className="mt-5 rounded-xl bg-blue-900 px-5 py-2.5 text-sm font-semibold text-white transition group-hover:bg-blue-800">
            Selecionar arquivos
          </span>

          <span className="mt-3 text-xs text-slate-400">
            Formato permitido: XML
          </span>

          <input
            id="xml-upload"
            type="file"
            accept=".xml"
            multiple
            className="hidden"
            onChange={(event) => {
              setArquivos(event.target.files)
              setErro('')
            }}
          />

        </label>


        {/* ARQUIVOS SELECIONADOS */}

        {arquivos && arquivos.length > 0 && (

          <div className="mt-5 rounded-xl border border-slate-200 bg-white p-4">

            <div className="flex items-center justify-between">

              <div>

                <p className="text-sm font-semibold text-slate-800">
                  Arquivos selecionados
                </p>

                <p className="mt-1 text-xs text-slate-500">
                  {arquivos.length} arquivo(s)
                </p>

              </div>

              <span className="rounded-full bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-700">
                {arquivos.length}
              </span>

            </div>

            <div className="mt-3 max-h-32 overflow-y-auto">

              {Array.from(arquivos).map((arquivo, indice) => (

                <div
                  key={indice}
                  className="flex items-center gap-2 border-t border-slate-100 py-2 text-sm text-slate-600"
                >

                  <span>
                    📄
                  </span>

                  <span className="truncate">
                    {arquivo.name}
                  </span>

                </div>

              ))}

            </div>

          </div>

        )}


        {/* BOTÃO PROCESSAR */}

        <div className="mt-5">

          <button
            type="button"
            onClick={processarArquivos}
            disabled={carregando || !arquivos?.length}
            className="w-full rounded-xl bg-blue-900 px-5 py-3 text-sm font-semibold text-white transition hover:bg-blue-800 disabled:cursor-not-allowed disabled:bg-slate-300"
          >

            {carregando
              ? 'Processando arquivos...'
              : 'Processar notas fiscais'
            }

          </button>

        </div>


        {/* ERRO */}

        {erro && (

          <div className="mt-4 rounded-xl border border-red-200 bg-red-50 px-4 py-3">

            <p className="text-sm font-medium text-red-700">
              {erro}
            </p>

          </div>

        )}

      </div>

    </section>
  )
}