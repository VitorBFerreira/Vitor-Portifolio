#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Análise logística demonstrativa. Usa apenas dados fictícios e CSVs."""
from __future__ import annotations

import argparse
import csv
import math
from collections import defaultdict
from pathlib import Path


def carregar_csv(caminho: Path, campos: set[str]) -> list[dict[str, str]]:
    with caminho.open(encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.DictReader(arquivo)
        faltantes = campos - set(leitor.fieldnames or [])
        if faltantes:
            raise ValueError(f"{caminho.name}: colunas ausentes: {', '.join(sorted(faltantes))}")
        return list(leitor)


def valor(numero: str, campo: str) -> float:
    try:
        resultado = float(str(numero).replace(",", "."))
    except ValueError as exc:
        raise ValueError(f"Valor inválido em {campo}: {numero!r}") from exc
    if not math.isfinite(resultado) or resultado < 0:
        raise ValueError(f"{campo} deve ser finito e não negativo")
    return resultado


def analisar(estoques: list[dict[str, str]],
            reservas: list[dict[str, str]],
            multiplos: list[dict[str, str]]) -> list[dict[str, object]]:
    """Consolida materiais e calcula reposição demonstrativa por múltiplos.

    Estoque útil = max(estoque_livre - comprometido, 0)
    Demanda líquida = max(soma(necessário) - soma(atendido), 0)
    Necessidade = ceil(max(demanda - estoque útil, 0) / múltiplo)
    Sugestão = min(necessidade, pallets completos disponíveis no destino)
    """
    estoque_por_material: dict[str, dict[str, float | str]] = {}
    for linha in estoques:
        material = linha["material"].strip()
        if not material or material in estoque_por_material:
            raise ValueError(f"Material vazio ou duplicado no estoque: {material!r}")
        estoque_por_material[material] = {
            "descricao": linha["descricao"],
            "origem": valor(linha["estoque_origem"], "estoque_origem"),
            "destino": valor(linha["estoque_destino"], "estoque_destino"),
            "comprometido": valor(linha["estoque_comprometido"], "estoque_comprometido"),
        }

    demanda = defaultdict(lambda: {"necessario": 0.0, "atendido": 0.0, "desvios": 0})
    for linha in reservas:
        mat = linha["material"].strip()
        if mat not in estoque_por_material:
            continue
        necessario = valor(linha["necessario"], "necessario")
        atendido = valor(linha["atendido"], "atendido")
        demanda[mat]["necessario"] += necessario
        demanda[mat]["atendido"] += atendido
        demanda[mat]["desvios"] += int(atendido > necessario + 1e-7)

    multiplo_por_material: dict[str, float] = {}
    divergentes: set[str] = set()
    for linha in multiplos:
        mat = linha["material"].strip()
        quantidade = valor(linha["kg_por_pallet"], "kg_por_pallet")
        if mat in multiplo_por_material and abs(multiplo_por_material[mat] - quantidade) > 1e-7:
            divergentes.add(mat)
        multiplo_por_material[mat] = quantidade

    resultado = []
    for mat, estoque in sorted(estoque_por_material.items()):
        if estoque["destino"] <= 0:
            continue
        m = multiplo_por_material.get(mat, 0)
        d = demanda[mat]
        util = max(float(estoque["origem"]) - float(estoque["comprometido"]), 0)
        pendente = max(d["necessario"] - d["atendido"], 0)
        diferenca = util - pendente
        necessidade_pallets = math.ceil(max(-diferenca, 0) / m - 1e-10) if m > 0 else 0
        disponiveis = math.floor(float(estoque["destino"]) / m + 1e-10) if m > 0 else 0
        pedido = min(necessidade_pallets, disponiveis)
        status = ("MULTIPLO_DIVERGENTE" if mat in divergentes else
                  "SEM_MULTIPLO" if m <= 0 else
                  "SEM_COBERTURA" if necessidade_pallets > disponiveis else
                  "REPOR" if pedido > 0 else "OK")
        if status in {"MULTIPLO_DIVERGENTE", "SEM_MULTIPLO"}:
            pedido = 0
        resultado.append({
            "material": mat, "descricao": estoque["descricao"],
            "estoque_util": round(util, 3),
            "demanda_liquida": round(pendente, 3),
            "diferenca": round(diferenca, 3),
            "kg_por_pallet": m,
            "pallets_sugeridos": pedido,
            "pallets_sem_cobertura": max(necessidade_pallets - disponiveis, 0),
            "reservas_com_desvio": d["desvios"],
            "status": status,
        })
    return resultado


def main() -> None:
    pasta = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="Demonstração pública de análise logística")
    parser.add_argument("--dados", type=Path, default=pasta / "exemplos")
    parser.add_argument("--saida", type=Path, default=pasta / "relatorio.csv")
    args = parser.parse_args()
    estoques = carregar_csv(args.dados / "estoques.csv",
                           {"material", "descricao", "estoque_origem", "estoque_destino", "estoque_comprometido"})
    reservas = carregar_csv(args.dados / "reservas.csv", {"material", "necessario", "atendido"})
    multiplos = carregar_csv(args.dados / "multiplos.csv", {"material", "kg_por_pallet"})
    resultado = analisar(estoques, reservas, multiplos)
    if not resultado:
        print("Nenhum material com estoque positivo no destino.")
        return
    args.saida.parent.mkdir(parents=True, exist_ok=True)
    with args.saida.open("w", encoding="utf-8-sig", newline="") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=list(resultado[0]))
        escritor.writeheader()
        escritor.writerows(resultado)
    print(f"Materiais: {len(resultado)} | Reposição sugerida: "
          f"{sum(int(r['pallets_sugeridos']) for r in resultado)} pallets")
    print(f"Relatório: {args.saida}")


if __name__ == "__main__":
    main()
