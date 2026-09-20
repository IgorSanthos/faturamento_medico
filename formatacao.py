def formatar_reais(valor):
    """
    Formata um valor numérico para o padrão brasileiro:
    R$ 1.234,56
    """
    return (
        f"R$ {valor:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )