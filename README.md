# Mini-Projeto
# Festa em Cena – Análise de pedidos de Halloween

Mini-Projeto Avaliativo – Módulo 1 (Machine Learning e Visão Computacional – Turma 04)

## Descrição do projeto

A Festa em Cena é uma rede **fictícia** que vende fantasias e acessórios de Halloween nos canais **Mercado**, **Loja física** e **Web**. Os registros têm problemas de qualidade (categorias vazias, pontuação indevida, canais escritos de formas diferentes, quantidades e preços inválidos, datas inválidas). O programa lê o CSV, trata esses problemas **sem alterar o arquivo original** e gera um relatório antes de comparar os períodos de venda.

**O que é uma linha:** um pedido de um único produto, que pode ter várias unidades.

**Quatro colunas:**
- `pedido_id`: identificador único do pedido.
- `canal_venda`: onde o pedido foi feito (Mercado, Loja física ou Web).
- `quantidade`: unidades do produto no pedido (não é número de pedidos).
- `data_venda`: data e hora do pedido, horário local de São Paulo.

### Regras adotadas
- **Categoria:** `strip()` + `lower()` + `re.sub(r"[^a-z\s]", "", ...)`, mantendo só letras e espaços (as categorias do CSV não têm acento). Vazia, ou vazia após a limpeza, vira `"sem categoria"`.
- **Canal:** padronizado para `Mercado`, `Loja física` e `Web`. Se não fosse reconhecido, ficaria sem canal e seria excluído da contagem (nenhum caso ocorreu).
- **Quantidade:** válida se for inteiro maior que zero. **Preço:** válido se preenchido e não negativo. Registros inválidos são **marcados**, nunca corrigidos nem preenchidos com 0, porque inventar valor distorceria qualquer análise futura.
- **Datas:** `data_venda` é convertida com `strptime("%Y-%m-%d %H:%M:%S")`. Inválida ou vazia é marcada e o processamento continua; não é trocada pela data de hoje. O texto original é preservado.
- **Entrega:** não alteramos status nem inventamos datas de entrega.

## Guia de execução

Arquivos necessários, na mesma pasta:
```
main.py
halloween_vendas.csv
```
Execute (Python 3, só biblioteca padrão):
```
python main.py
```

## Resultados (base com 1.500 pedidos)

| Item | Resultado |
|---|---|
| Linhas lidas | 1.500 |
| Categorias vazias preenchidas | 18 |
| Categorias não vazias alteradas (além de maiúsculas/minúsculas) | 131 |
| Canais com escrita corrigida | 45 |
| `quantidade` inválida | 7 |
| `preco_unitario` inválido | 12 |
| Pedidos com problema numérico (sem dupla contagem) | 19 |
| Datas de venda inválidas | 4 |
| Pedidos cancelados | 109 |

### Conclusão sobre entrega sem data
Há 143 pedidos sem `data_entrega`: **109 são cancelados e 34 têm outro status** (por exemplo, pedido 1170 e pedido 990, ambos Concluído). Portanto, a hipótese "todo pedido sem data de entrega é cancelado" é **falsa nesta base**. Os 109 cancelados, por sua vez, estão todos sem entrega.

### Descoberta 1 – por canal
- **Número:** Web 666 pedidos (44,4%), Loja física 551 (36,7%) e Mercado 283 (18,9%), somando 1.500 (nenhum excluído).
- **Interpretação:** o site concentra o maior número de pedidos registrados; o Mercado tem menos da metade dos pedidos da Web.
- **Limitação:** são pedidos registrados, de todos os status, e não receita nem vendas concluídas. Pedidos grandes ou pequenos pesam igual, e a base é fictícia, então não representa o mercado real.

### Descoberta 2 – por período (ano-mês)
- **Número:** outubro concentra os pedidos nos dois anos: 393 em 2024-10 e 410 em 2025-10, contra 62 a 104 em agosto e setembro. Total de 748 pedidos em cada ano (4 pedidos excluídos por data inválida).
- **Interpretação:** as vendas se concentram perto do Halloween (31/10), com queda em novembro (174 em 2024 e 182 em 2025).
- **Limitação:** só há quatro meses por ano, então não dá para falar de sazonalidade do ano inteiro; e as contagens misturam pedidos cancelados e devolvidos.

## Reflexão: qualidade dos dados e Machine Learning

Dados com categorias inconsistentes, valores ausentes ou datas inválidas fazem o modelo aprender padrões errados: "Fantasia" e "FANTASIA!!!" seriam tratadas como categorias diferentes. A limpeza é, portanto, uma etapa essencial antes do ML. Mas **limpar não basta para evitar overfitting ou underfitting**: isso também depende de a base ser representativa, da escolha do modelo e de uma avaliação adequada (por exemplo, com dados separados para teste).
