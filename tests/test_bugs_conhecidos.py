"""Bugs conhecidos da versão 0.3.

Cada teste descreve o comportamento CORRETO e hoje falha, por isso está marcado
com @expectedFailure. Quando um bug for corrigido, o unittest avisa com
"unexpected success": aí é só apagar o decorador.
"""
import json
import os
import tempfile
import unittest
from datetime import date

from finance_fjl import (Categoria, ContaCorrente, ContaPoupanca, Formato, Receita, Repositorio,
                         Usuario)

HOJE = date(2026, 11, 5)
SALARIO = Categoria("Salário", Categoria.RECEITA)


class TestBugsConhecidos(unittest.TestCase):
    def setUp(self):
        self.usuario = Usuario("Ana Souza", "ana@email.com")
        self.corrente = self.usuario.adicionar_conta(ContaCorrente("Principal"))
        self.poupanca = self.usuario.adicionar_conta(ContaPoupanca("Reserva"))

    @unittest.expectedFailure
    def test_b1_transferencia_nao_conta_no_resumo_do_mes(self):
        self.corrente.lancar(Receita(1000, HOJE, "Salário", SALARIO))
        self.usuario.transferir(self.corrente, self.poupanca, 400, HOJE)
        resumo = self.usuario.resumo_mes(2026, 11)
        self.assertEqual(resumo, {"receitas": 1000, "despesas": 0})

    @unittest.expectedFailure
    def test_b2_ponto_de_milhar(self):
        self.assertEqual(Formato.ler_valor("1.250"), 1250)

    @unittest.expectedFailure
    def test_b2_valor_completo_no_formato_brasileiro(self):
        self.assertEqual(Formato.ler_valor("1.250,90"), 1250.9)

    @unittest.expectedFailure
    def test_b3_arredondamento_nos_centavos(self):
        self.corrente.depositar(0.30)
        self.corrente.sacar(0.10)
        self.corrente.sacar(0.20)       # a tela mostra R$ 0,20, mas o sistema recusa
        self.assertEqual(self.corrente.saldo, 0)

    @unittest.expectedFailure
    def test_b4_nao_exclui_conta_com_saldo(self):
        self.poupanca.depositar(500)
        with self.assertRaises(ValueError):
            self.usuario.remover_conta(self.poupanca)

    @unittest.expectedFailure
    def test_b5_nao_aceita_duas_contas_com_o_mesmo_nome(self):
        with self.assertRaises(ValueError):
            self.usuario.adicionar_conta(ContaCorrente("Principal"))

    @unittest.expectedFailure
    def test_b6_poupanca_rende_uma_vez_por_mes(self):
        self.poupanca.depositar(1000)
        self.poupanca.render(HOJE)
        with self.assertRaises(ValueError):
            self.poupanca.render(HOJE)

    @unittest.expectedFailure
    def test_b7_excluir_transferencia_desfaz_os_dois_lados(self):
        self.corrente.depositar(1000)
        saida, _entrada = self.usuario.transferir(self.corrente, self.poupanca, 400, HOJE)
        self.usuario.excluir_lancamento(self.corrente, saida)
        self.assertEqual(self.usuario.saldo_total(), 1000)

    @unittest.expectedFailure
    def test_b9_arquivo_corrompido_gera_mensagem_clara(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminho = os.path.join(pasta, "dados.json")
            with open(caminho, "w", encoding="utf-8") as arquivo:
                arquivo.write("{ isto não é JSON")
            try:
                Repositorio(caminho).carregar()
            except json.JSONDecodeError:
                self.fail("o erro técnico do JSON chega até o usuário")
            except ValueError:
                pass

    @unittest.expectedFailure
    def test_b10_mensagem_de_valor_invalido_em_portugues(self):
        with self.assertRaises(ValueError) as contexto:
            Formato.ler_valor("abc")
        self.assertIn("Valor inválido", str(contexto.exception))

    @unittest.expectedFailure
    def test_b10_mensagem_de_data_invalida_em_portugues(self):
        with self.assertRaises(ValueError) as contexto:
            Formato.ler_data("32/10/2026")
        self.assertIn("Data inválida", str(contexto.exception))


if __name__ == "__main__":
    unittest.main()
