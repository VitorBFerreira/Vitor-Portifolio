import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analise_logistica import analisar


class AnaliseLogisticaTests(unittest.TestCase):
    def setUp(self):
        self.estoques = [{
            "material": "MAT-001", "descricao": "Material teste",
            "estoque_origem": "100", "estoque_destino": "900",
            "estoque_comprometido": "20",
        }]
        self.multiplos = [{"material": "MAT-001", "kg_por_pallet": "100"}]

    def test_soma_necessidades_e_atendimentos_antes_do_piso(self):
        reservas = [
            {"material": "MAT-001", "necessario": "300", "atendido": "350"},
            {"material": "MAT-001", "necessario": "500", "atendido": "0"},
        ]
        resultado = analisar(self.estoques, reservas, self.multiplos)[0]
        self.assertEqual(resultado["demanda_liquida"], 450)
        self.assertEqual(resultado["estoque_util"], 80)
        self.assertEqual(resultado["pallets_sugeridos"], 4)
        self.assertEqual(resultado["reservas_com_desvio"], 1)

    def test_limita_reposicao_ao_estoque_destino(self):
        resultado = analisar(self.estoques, [{
            "material": "MAT-001", "necessario": "2000", "atendido": "0"
        }], self.multiplos)[0]
        self.assertEqual(resultado["pallets_sugeridos"], 9)
        self.assertEqual(resultado["status"], "SEM_COBERTURA")

    def test_bloqueia_multiplo_divergente(self):
        resultado = analisar(self.estoques, [{
            "material": "MAT-001", "necessario": "1000", "atendido": "0"
        }], self.multiplos + [{"material": "MAT-001", "kg_por_pallet": "120"}])[0]
        self.assertEqual(resultado["pallets_sugeridos"], 0)
        self.assertEqual(resultado["status"], "MULTIPLO_DIVERGENTE")


if __name__ == "__main__":
    unittest.main()
