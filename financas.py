from datetime import datetime

# =========================
# Utilidades / Validações
# =========================

def parse_data_iso(data_str):
    """
    Recebe uma string no formato YYYY-MM-DD e retorna um objeto date.
    Levanta ValueError se for inválida.
    """
    return datetime.strptime(data_str, "%Y-%m-%d").date()


def input_nao_vazio(msg):
    while True:
        s = input(msg).strip()
        if s:
            return s
        print("Entrada vazia. Tente novamente.")


def input_float_positivo(msg):
    while True:
        raw = input(msg).strip().replace(",", ".")
        try:
            valor = float(raw)
            if valor <= 0:
                print("Digite um valor maior que zero.")
                continue
            return valor
        except ValueError:
            print("Valor inválido. Ex: 10.50")


def input_data(msg):
    while True:
        raw = input(msg).strip()
        try:
            return parse_data_iso(raw)
        except ValueError:
            print("Data inválida. Use o formato YYYY-MM-DD. Ex: 2026-06-19")


def input_int_intervalo(msg, minimo, maximo):
    while True:
        raw = input(msg).strip()
        if not raw.isdigit():
            print("Digite um número válido.")
            continue
        n = int(raw)
        if n < minimo or n > maximo:
            print(f"Escolha um número entre {minimo} e {maximo}.")
            continue
        return n


def pausar():
    input("\nPressione ENTER para continuar...")


# =========================
# Regras / Operações
# =========================

def proximo_id(transacoes):
    if not transacoes:
        return 1
    maior = max(t["id"] for t in transacoes)
    return maior + 1


def adicionar_transacao(transacoes):
    print("\n== Adicionar transação ==")
    print("1) Receita")
    print("2) Despesa")
    tipo_op = input_int_intervalo("Escolha o tipo: ", 1, 2)

    if tipo_op == 1:
        tipo = "receita"
    else:
        tipo = "despesa"

    valor = input_float_positivo("Valor (ex: 10.50): ")
    categoria = input_nao_vazio("Categoria (ex: alimentação, transporte): ").lower()
    data = input_data("Data (YYYY-MM-DD): ")
    descricao = input_nao_vazio("Descrição: ")

    transacao = {
        "id": proximo_id(transacoes),
        "tipo": tipo,
        "valor": valor,
        "categoria": categoria,
        "data": data,  # objeto date
        "descricao": descricao
    }

    transacoes.append(transacao)
    print(f"Transação adicionada com ID {transacao['id']}.")


def listar_transacoes(transacoes, filtros=None):
    filtros = filtros or {}
    itens = transacoes

    tipo = filtros.get("tipo")
    if tipo:
        itens = [t for t in itens if t["tipo"] == tipo]

    categoria = filtros.get("categoria")
    if categoria:
        itens = [t for t in itens if t["categoria"] == categoria]

    data_ini = filtros.get("data_ini")
    if data_ini:
        itens = [t for t in itens if t["data"] >= data_ini]

    data_fim = filtros.get("data_fim")
    if data_fim:
        itens = [t for t in itens if t["data"] <= data_fim]

    if not itens:
        print("\nNenhuma transação encontrada com os filtros atuais.")
        return

    print("\n== Transações ==")
    print("ID | Data       | Tipo    | Valor    | Categoria     | Descrição")
    print("-" * 72)
    for t in sorted(itens, key=lambda x: (x["data"], x["id"])):
        data_str = t["data"].strftime("%Y-%m-%d")
        print(f"{t['id']:>2} | {data_str} | {t['tipo']:<7} | {t['valor']:>7.2f} | {t['categoria']:<12} | {t['descricao']}")


def remover_transacao(transacoes):
    if not transacoes:
        print("\nNão há transações para remover.")
        return

    listar_transacoes(transacoes)
    tid = input_int_intervalo("\nDigite o ID para remover: ", 1, 10**9)

    idx = None
    for i, t in enumerate(transacoes):
        if t["id"] == tid:
            idx = i
            break

    if idx is None:
        print("ID não encontrado.")
        return

    removida = transacoes.pop(idx)
    print(f"Removida: ID {removida['id']} ({removida['tipo']} - {removida['valor']:.2f})")


def resumo(transacoes, data_ini=None, data_fim=None):
    itens = transacoes
    if data_ini:
        itens = [t for t in itens if t["data"] >= data_ini]
    if data_fim:
        itens = [t for t in itens if t["data"] <= data_fim]

    total_receitas = sum(t["valor"] for t in itens if t["tipo"] == "receita")
    total_despesas = sum(t["valor"] for t in itens if t["tipo"] == "despesa")
    saldo = total_receitas - total_despesas

    print("\n== Resumo ==")
    if data_ini or data_fim:
        di = data_ini.strftime("%Y-%m-%d") if data_ini else "..."
        df = data_fim.strftime("%Y-%m-%d") if data_fim else "..."
        print(f"Período: {di} até {df}")
    print(f"Total de receitas: R$ {total_receitas:.2f}")
    print(f"Total de despesas: R$ {total_despesas:.2f}")
    print(f"Saldo:            R$ {saldo:.2f}")

    if saldo < 0:
        print("Atenção: saldo negativo. Considere revisar despesas.")
    elif saldo == 0:
        print("Saldo zerado. Você está no ponto de equilíbrio.")
    else:
        print("Bom: saldo positivo!")


def relatorio_por_categoria(transacoes, tipo=None):
    itens = transacoes
    if tipo in ("receita", "despesa"):
        itens = [t for t in itens if t["tipo"] == tipo]

    if not itens:
        print("\nSem dados para relatório por categoria.")
        return

    acumulado = {}
    for t in itens:
        cat = t["categoria"]
        acumulado[cat] = acumulado.get(cat, 0.0) + t["valor"]

    print("\n== Relatório por categoria ==")
    if tipo:
        print(f"Tipo: {tipo}")

    print("Categoria        | Total")
    print("-" * 28)
    for cat, total in sorted(acumulado.items(), key=lambda x: x[1], reverse=True):
        print(f"{cat:<15} | R$ {total:.2f}")


def top_despesas(transacoes, n=5):
    despesas = [t for t in transacoes if t["tipo"] == "despesa"]
    if not despesas:
        print("\nSem despesas para mostrar.")
        return

    despesas_ordenadas = sorted(despesas, key=lambda t: t["valor"], reverse=True)
    n = min(n, len(despesas_ordenadas))

    print(f"\n== Top {n} despesas ==")
    print("ID | Data       | Valor    | Categoria     | Descrição")
    print("-" * 64)
    for t in despesas_ordenadas[:n]:
        data_str = t["data"].strftime("%Y-%m-%d")
        print(f"{t['id']:>2} | {data_str} | {t['valor']:>7.2f} | {t['categoria']:<12} | {t['descricao']}")


# =========================
# Menus (CLI)
# =========================

def menu_listagem(transacoes):
    while True:
        print("\n== Listagem / Filtros ==")
        print("1) Listar tudo")
        print("2) Filtrar por tipo (receita/despesa)")
        print("3) Filtrar por categoria")
        print("4) Filtrar por período (data inicial e final)")
        print("0) Voltar")
        op = input_int_intervalo("Escolha: ", 0, 4)

        if op == 0:
            return

        if op == 1:
            listar_transacoes(transacoes)
            pausar()

        elif op == 2:
            print("\n1) receita\n2) despesa")
            t = input_int_intervalo("Escolha: ", 1, 2)
            tipo = "receita" if t == 1 else "despesa"
            listar_transacoes(transacoes, {"tipo": tipo})
            pausar()

        elif op == 3:
            cat = input_nao_vazio("Categoria: ").lower()
            listar_transacoes(transacoes, {"categoria": cat})
            pausar()

        elif op == 4:
            di = input_data("Data inicial (YYYY-MM-DD): ")
            df = input_data("Data final   (YYYY-MM-DD): ")
            if di > df:
                print("Período inválido: data inicial maior que data final.")
            else:
                listar_transacoes(transacoes, {"data_ini": di, "data_fim": df})
            pausar()


def menu_relatorios(transacoes):
    while True:
        print("\n== Relatórios ==")
        print("1) Resumo (total receitas, despesas, saldo)")
        print("2) Relatório por categoria (tudo)")
        print("3) Relatório por categoria (apenas despesas)")
        print("4) Top 5 despesas")
        print("0) Voltar")
        op = input_int_intervalo("Escolha: ", 0, 4)

        if op == 0:
            return

        if op == 1:
            print("\nFiltrar por período?")
            print("1) Sim")
            print("2) Não")
            sub = input_int_intervalo("Escolha: ", 1, 2)
            if sub == 1:
                di = input_data("Data inicial (YYYY-MM-DD): ")
                df = input_data("Data final   (YYYY-MM-DD): ")
                if di > df:
                    print("Período inválido: data inicial maior que data final.")
                else:
                    resumo(transacoes, di, df)
            else:
                resumo(transacoes)
            pausar()

        elif op == 2:
            relatorio_por_categoria(transacoes)
            pausar()

        elif op == 3:
            relatorio_por_categoria(transacoes, tipo="despesa")
            pausar()

        elif op == 4:
            top_despesas(transacoes, n=5)
            pausar()


def carregar_exemplos():
    return [
        {"id": 1, "tipo": "receita", "valor": 2500.00, "categoria": "salário", "data": parse_data_iso("2026-06-01"), "descricao": "salário"},
        {"id": 2, "tipo": "despesa", "valor": 120.50, "categoria": "mercado", "data": parse_data_iso("2026-06-02"), "descricao": "compras da semana"},
        {"id": 3, "tipo": "despesa", "valor": 65.90, "categoria": "transporte", "data": parse_data_iso("2026-06-03"), "descricao": "combustível"},
        {"id": 4, "tipo": "despesa", "valor": 39.90, "categoria": "assinaturas", "data": parse_data_iso("2026-06-05"), "descricao": "streaming"},
        {"id": 5, "tipo": "receita", "valor": 300.00, "categoria": "freela", "data": parse_data_iso("2026-06-10"), "descricao": "serviço pontual"},
    ]


def main():
    print("Finanças CLI - Controle simples de receitas e despesas")
    print("Carregar dados de exemplo?")
    print("1) Sim")
    print("2) Não (começar vazio)")
    op = input_int_intervalo("Escolha: ", 1, 2)

    if op == 1:
        transacoes = carregar_exemplos()
    else:
        transacoes = []

    while True:
        print("\n== Menu Principal ==")
        print("1) Adicionar transação")
        print("2) Listar / Filtrar transações")
        print("3) Remover transação")
        print("4) Relatórios")
        print("0) Sair")
        escolha = input_int_intervalo("Escolha: ", 0, 4)

        if escolha == 0:
            print("Saindo... até mais!")
            break
        elif escolha == 1:
            adicionar_transacao(transacoes)
            pausar()
        elif escolha == 2:
            menu_listagem(transacoes)
        elif escolha == 3:
            remover_transacao(transacoes)
            pausar()
        elif escolha == 4:
            menu_relatorios(transacoes)


if __name__ == "__main__":
    main()
