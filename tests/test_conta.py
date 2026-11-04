"""Testes das contas: saldo privado, limite, poupança, polimorfismo e transferência."""
import unittest
from datetime import date

from finance_fjl import (Categoria, Conta, ContaCorrente, ContaPoupanca, Despesa, Receita,
                         SaldoInsuficienteError)

HOJE = date(2026, 11, 5)
LAZER = Categoria("Lazer", Categoria.DESPESA)
SALARIO = Categoria("Salário", Categoria.RECEITA)


class TestSaldoPrivado(unittest.TestCase):
    """O diferencial do projeto: o saldo só muda por depositar() e sacar()."""

    def setUp(self):
        self.conta = ContaCorrente("Principal", limite=500)

    def test_conta_comeca_zerada(self):
        self.assertEqual(self.conta.saldo, 0.0)

    def test_saldo_e_somente_leitura(self):
        with self.assertRaises(AttributeError):
            self.conta.saldo = 1_000_000

    def test_atributo_privado_nao_acessivel_pelo_nome(self):
        with self.assertRaises(AttributeError):
            self.conta.__saldo
        self.assertIn("_Conta__saldo", vars(self.conta))

    def test_metodo_privado_validar_valor(self):
        self.assertFalse(hasattr(self.conta, "__validar_valor"))
        self.assertTrue(hasattr(self.conta, "_Conta__validar_valor"))

    def test_depositar_e_sacar(self):
        self.conta.depositar(1200)
        self.conta.sacar(200)
        self.assertEqual(self.conta.saldo, 1000)

    def test_valores_invalidos_nao_mudam_o_saldo(self):
        for valor in (0, -10, "100", None, True):
            with self.assertRaises(ValueError):
                self.conta.depositar(valor)
        self.assertEqual(self.conta.saldo, 0)

    def test_conta_e_abstrata(self):
        with self.assertRaises(TypeError):
            Conta("Qualquer")


class TestContaCorrente(unittest.TestCase):
    def test_usa_o_limite_ate_o_fim(self):
        conta = ContaCorrente("Principal", limite=500)
        conta.depositar(1200)
        conta.sacar(1500)
        self.assertEqual(conta.saldo, -300)
        self.assertEqual(conta.disponivel_para_saque(), 200)

    def test_passar_do_limite_gera_erro_e_nao_muda_o_saldo(self):
        conta = ContaCorrente("Principal", limite=500)
        conta.depositar(1200)
        conta.sacar(1500)
        with self.assertRaises(SaldoInsuficienteError) as contexto:
            conta.sacar(300)
        self.assertEqual(contexto.exception.disponivel, 200)
        self.assertEqual(conta.saldo, -300)

    def test_limite_nao_pode_ser_menor_que_o_usado(self):
        conta = ContaCorrente("Principal", limite=500)
        conta.sacar(300)
        with self.assertRaises(ValueError):
            conta.limite = 100


class TestContaPoupanca(unittest.TestCase):
    def test_nao_fica_negativa(self):
        poupanca = ContaPoupanca("Reserva")
        poupanca.depositar(100)
        with self.assertRaises(SaldoInsuficienteError):
            poupanca.sacar(100.01)

    def test_render_entra_como_receita(self):
        poupanca = ContaPoupanca("Reserva", taxa_rendimento=0.01)
        poupanca.depositar(1000)
        receita = poupanca.render(HOJE)
        self.assertIsInstance(receita, Receita)
        self.assertEqual(poupanca.saldo, 1010)

    def test_sem_saldo_nao_rende(self):
        with self.assertRaises(ValueError):
            ContaPoupanca("Reserva").render(HOJE)

    def test_taxa_invalida(self):
        with self.assertRaises(ValueError):
            ContaPoupanca("Reserva", taxa_rendimento=0.5)


class TestLancamentosETransferencias(unittest.TestCase):
    def setUp(self):
        self.origem = ContaCorrente("Principal")
        self.destino = ContaPoupanca("Reserva")
        self.origem.lancar(Receita(1000, HOJE, "Salário", SALARIO))

    def test_polimorfismo_em_lancar(self):
        self.origem.lancar(Despesa(300, HOJE, "Show", LAZER))
        self.assertEqual(self.origem.saldo, 700)
        self.assertEqual(len(self.origem.historico), 2)

    def test_despesa_sem_saldo_nao_entra_no_historico(self):
        with self.assertRaises(SaldoInsuficienteError):
            self.origem.lancar(Despesa(1500, HOJE, "Show", LAZER))
        self.assertEqual(len(self.origem.historico), 1)

    def test_excluir_lancamento_desfaz_o_efeito(self):
        despesa = self.origem.lancar(Despesa(300, HOJE, "Show", LAZER))
        self.origem.remover_lancamento(despesa)
        self.assertEqual(self.origem.saldo, 1000)
        self.assertEqual(len(self.origem.historico), 1)

    def test_transferencia_move_o_valor(self):
        self.origem.transferir(400, self.destino, HOJE)
        self.assertEqual(self.origem.saldo, 600)
        self.assertEqual(self.destino.saldo, 400)

    def test_transferencia_sem_saldo_nao_muda_nada(self):
        with self.assertRaises(SaldoInsuficienteError):
            self.origem.transferir(5000, self.destino, HOJE)
        self.assertEqual(self.origem.saldo, 1000)
        self.assertEqual(self.destino.saldo, 0)

    def test_transferencia_para_a_mesma_conta(self):
        with self.assertRaises(ValueError):
            self.origem.transferir(10, self.origem, HOJE)


if __name__ == "__main__":
    unittest.main()
