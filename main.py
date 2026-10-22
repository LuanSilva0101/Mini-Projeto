"""
Mini-Projeto Avaliativo - Módulo 1 - Festa em Cena (Halloween)
"""
import csv
import re
from collections import Counter
from datetime import datetime

ARQUIVO = "halloween_vendas.csv"
FORMATO_DATA = "%Y-%m-%d %H:%M:%S"

# Mapa para padronizar canais (chave = texto limpo, em minúsculas)
CANAIS = {"mercado": "Mercado", "loja física": "Loja física", "web": "Web"}


def ler_csv(caminho):
    """Lê o CSV com DictReader. Todos os campos chegam como texto."""
    with open(caminho, mode="r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter=","))


def limpar_categoria(texto):
    """
    strip + lower + re.sub.
    O regex mantém só letras e espaços: as categorias do CSV não têm acento,
    então [^a-z ] remove '!!!' e outras pontuações. Depois colapsamos espaços
    repetidos. Se sobrar vazio, devolve 'sem categoria'.
    """
    limpo = texto.strip().lower()
    limpo = re.sub(r"[^a-z\s]", "", limpo)
    limpo = re.sub(r"\s+", " ", limpo).strip()
    return limpo if limpo else "sem categoria"


def padronizar_canal(texto):
    """Devolve Mercado, Loja física ou Web; None se não for reconhecido
    (não inventamos canal)."""
    return CANAIS.get(texto.strip().lower())


def validar_quantidade(texto):
    """Válida = inteiro > 0. Não corrigimos valores inválidos."""
    try:
        return int(texto.strip()) > 0
    except ValueError:
        return False


def validar_preco(texto):
    """Válido = preenchido, numérico e >= 0. Preço ausente NÃO vira 0."""
    if texto.strip() == "":
        return False
    try:
        return float(texto) >= 0
    except ValueError:
        return False


def converter_data(texto):
    """Converte data_venda. Retorna dict com partes ou None se inválida/vazia.
    O texto original é preservado fora desta função."""
    try:
        dt = datetime.strptime(texto.strip(), FORMATO_DATA)
    except ValueError:
        return None
    return {
        "ano": dt.year, "mes": dt.month, "dia": dt.day, "hora": dt.hour,
        "br": dt.strftime("%d/%m/%Y"),
        "ano_mes": dt.strftime("%Y-%m"),
    }


# ------------------------------------------------------------ Processamento
def processar(registros):
    """Percorre os registros uma vez, sem alterar os originais."""
    tratados = []
    c = Counter()
    pedidos_numericos_afetados = set()
    entrega_cancelados = 0
    entrega_outros = []

    for r in registros:
        t = dict(r)  # cópia: o original fica intacto
        c["linhas"] += 1

        # --- categoria
        original = r["categoria"]
        t["categoria_limpa"] = limpar_categoria(original)
        if original.strip() == "":
            c["cat_vazia_preenchida"] += 1
        elif original != t["categoria_limpa"]:
            c["cat_nao_vazia_alterada"] += 1
            # alteração "real": além de apenas trocar maiúsculas por minúsculas
            if original.lower() != t["categoria_limpa"]:
                c["cat_alterada_por_pontuacao_ou_espaco"] += 1
            if t["categoria_limpa"] == "sem categoria":
                c["cat_virou_vazia_apos_regex"] += 1

        # --- canal
        t["canal_padrao"] = padronizar_canal(r["canal_venda"])
        if t["canal_padrao"] is None:
            c["canal_nao_reconhecido"] += 1
        elif r["canal_venda"] != t["canal_padrao"]:
            c["canal_alterado"] += 1

        # --- quantidade e preço (marcamos, não corrigimos)
        t["qtd_ok"] = validar_quantidade(r["quantidade"])
        t["preco_ok"] = validar_preco(r["preco_unitario"])
        if not t["qtd_ok"]:
            c["qtd_invalida"] += 1
        if not t["preco_ok"]:
            c["preco_invalido"] += 1
        if not (t["qtd_ok"] and t["preco_ok"]):
            pedidos_numericos_afetados.add(r["pedido_id"])  # sem dupla contagem

        # --- data da venda
        partes = converter_data(r["data_venda"])
        t["data_partes"] = partes
        if partes is None:
            c["data_invalida"] += 1

        # --- cancelados e entrega sem data
        cancelado = r["status_pedido"].strip() == "Cancelado"
        if cancelado:
            c["cancelados"] += 1
        if r["data_entrega"].strip() == "":
            if cancelado:
                entrega_cancelados += 1
            else:
                entrega_outros.append(r)

        tratados.append(t)

    c["pedidos_numericos_afetados"] = len(pedidos_numericos_afetados)
    return tratados, c, entrega_cancelados, entrega_outros


def contar_por_canal(tratados):
    cont = Counter(t["canal_padrao"] for t in tratados if t["canal_padrao"])
    excluidos = sum(1 for t in tratados if t["canal_padrao"] is None)
    return cont, excluidos


def contar_por_ano_mes(tratados):
    cont = Counter(t["data_partes"]["ano_mes"] for t in tratados if t["data_partes"])
    excluidos = sum(1 for t in tratados if t["data_partes"] is None)
    return cont, excluidos


# ---------------------------------------------------------------- Relatório
def mostrar_relatorio(registros, tratados, c, ent_canc, ent_outros):
    print("=== RELATÓRIO DE STATUS ===")
    print(f"Linhas lidas: {c['linhas']}")
    print("\n-- Três primeiros registros (originais) --")
    for r in registros[:3]:
        print(r)

    print("\n-- Categorias --")
    print(f"Vazias preenchidas com 'sem categoria': {c['cat_vazia_preenchida']}")
    print(f"Não vazias alteradas além da caixa (espaços/pontuação): {c['cat_alterada_por_pontuacao_ou_espaco']}")
    print(f"  (total com texto diferente do original, contando só minúsculas: {c['cat_nao_vazia_alterada']})")
    print(f"Viraram vazias após o regex: {c['cat_virou_vazia_apos_regex']}")
    print("Exemplos antes -> depois:")
    for orig in ["  FANTASIA!!!  ", " Acessorio ", ""]:
        print(f"  {orig!r} -> {limpar_categoria(orig)!r}")
    print(f"Canais alterados: {c['canal_alterado']} | não reconhecidos: {c['canal_nao_reconhecido']}")

    print("\n-- Problemas numéricos --")
    print(f"quantidade inválida: {c['qtd_invalida']}")
    print(f"preco_unitario inválido: {c['preco_invalido']}")
    print(f"Pedidos afetados (sem somar sobreposição): {c['pedidos_numericos_afetados']}")

    print("\n-- Datas de venda --")
    print(f"Inválidas ou vazias: {c['data_invalida']}")
    ex = next(t for t in tratados if t["data_partes"])
    print(f"Exemplo: {ex['data_venda']} -> {ex['data_partes']['br']} (ano {ex['data_partes']['ano']}, hora {ex['data_partes']['hora']})")

    print("\n-- Entrega sem data x status --")
    print(f"Total de cancelados: {c['cancelados']}")
    print(f"Sem entrega e Cancelado: {ent_canc}")
    print(f"Sem entrega e outro status: {len(ent_outros)}")
    for r in ent_outros[:3]:
        print(f"  ex.: pedido {r['pedido_id']} | status {r['status_pedido']} | venda {r['data_venda']}")
    print("Hipótese 'todo pedido sem entrega é cancelado':",
          "FALSA na base" if ent_outros else "verdadeira na base")

    por_canal, exc_canal = contar_por_canal(tratados)
    print(f"\n-- Pedidos por canal (todos os status; excluídos: {exc_canal}) --")
    for k, v in por_canal.most_common():
        print(f"  {k}: {v}")

    por_mes, exc_mes = contar_por_ano_mes(tratados)
    print(f"\n-- Pedidos por ano-mês (todos os status; excluídos por data inválida: {exc_mes}) --")
    for k in sorted(por_mes):
        print(f"  {k}: {por_mes[k]}")


def main():
    registros = ler_csv(ARQUIVO)
    tratados, c, ent_canc, ent_outros = processar(registros)
    mostrar_relatorio(registros, tratados, c, ent_canc, ent_outros)


if __name__ == "__main__":
    main()
