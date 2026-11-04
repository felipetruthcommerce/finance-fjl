"""Testes de Transacao, Categoria, Usuario, Formato e Repositorio (JSON)."""
import os
import tempfile
import unittest
from datetime import date

from finance_fjl import (Categoria, ContaCorrente, ContaPoupanca, Despesa, Formato, Receita,
                         Repositorio, Transacao, Usuario)

HOJE = date(2026, 11, 5)
LAZER = Categoria("Lazer", Categoria.DESPESA)
SALARIO = Categoria("Salário", Categoria.RECEITA)


class TestTransacao(unittest.TestCase):
    def test_transacao_e_abstrata(self):
        with self.assertRaises(TypeError):
            Transacao(10, HOJE, "X", LAZER)

    def test_valor_invalido(self):
        for valor in (0, -5, "10"):
            with self.assertRaises(ValueError):
                Despesa(valor, HOJE, "X", LAZER)

    def test_descricao_vazia(self):
        with self.assertRaises(ValueError):
            Receita(10, HOJE, "   ", SALARIO)

    def test_forma_de_pagamento_invalida(self):
        with self.assertRaises(ValueError):
            Despesa(10, HOJE, "X", LAZER, "Cheque")

    def test_valor_com_sinal(self):
        self.assertEqual(Receita(10, HOJE, "X", SALARIO).valor_com_sinal(), 10)
        self.assertEqual(Despesa(10, HOJE, "X", LAZER).valor_com_sinal(), -10)


class TestCategoria(unittest.TestCase):
    def test_iguais_por_nome_e_tipo(self):
        self.assertEqual(Categoria("lazer", Categoria.DESPESA), LAZER)
        self.assertNotEqual(Categoria("Lazer", Categoria.RECEITA), LAZER)

    def test_padroes_tem_os_dois_tipos(self):
        tipos = {c.tipo for c in Categoria.padroes()}
        self.assertTrue({Categoria.RECEITA, Categoria.DESPESA} <= tipos)


class TestUsuario(unittest.TestCase):
    def setUp(self):
        self.usuario = Usuario("Ana Souza", "ana@email.com")
        self.corrente = self.usuario.adicionar_conta(ContaCorrente("Principal"))
        self.poupanca = self.usuario.adicionar_conta(ContaPoupanca("Reserva"))
        self.corrente.lancar(Receita(1000, HOJE, "Salário", SALARIO))

    def test_nome_obrigatorio(self):
        with self.assertRaises(ValueError):
            Usuario("  ", "ana@email.com")

    def test_saldo_total_soma_as_contas(self):
        self.poupanca.depositar(250)
        self.assertEqual(self.usuario.saldo_total(), 1250)

    def test_nao_remove_a_unica_conta(self):
        self.usuario.remover_conta(self.poupanca)
        with self.assertRaises(ValueError):
            self.usuario.remover_conta(self.corrente)

    def test_lancamentos_do_mais_recente_ao_mais_antigo(self):
        self.corrente.lancar(Despesa(50, date(2026, 11, 7), "Cinema", LAZER))
        self.corrente.lancar(Despesa(20, date(2026, 11, 6), "Lanche", LAZER))
        datas = [t.data for _, t in self.usuario.lancamentos()]
        self.assertEqual(datas, sorted(datas, reverse=True))

    def test_resumo_do_mes(self):
        self.corrente.lancar(Despesa(300, HOJE, "Show", LAZER))
        self.corrente.lancar(Despesa(99, date(2026, 10, 1), "Mês anterior", LAZER))
        resumo = self.usuario.resumo_mes(2026, 11)
        self.assertEqual(resumo, {"receitas": 1000, "despesas": 300})


class TestFormato(unittest.TestCase):
    def test_moeda(self):
        self.assertEqual(Formato.moeda(1234.5), "R$ 1.234,50")
        self.assertEqual(Formato.moeda(-10), "-R$ 10,00")

    def test_ler_valor_com_virgula(self):
        self.assertEqual(Formato.ler_valor("150,90"), 150.9)

    def test_ler_data(self):
        self.assertEqual(Formato.ler_data("05/11/2026"), HOJE)

    def test_data(self):
        self.assertEqual(Formato.data(HOJE), "05/11/2026")


class TestRepositorio(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()
        self.addCleanup(self.pasta.cleanup)
        self.repositorio = Repositorio(os.path.join(self.pasta.name, "dados.json"))

    def test_primeiro_uso_devolve_none(self):
        self.assertFalse(self.repositorio.existe())
        self.assertIsNone(self.repositorio.carregar())

    def test_salva_e_carrega_igual(self):
        usuario = Usuario("Ana Souza", "ana@email.com")
        corrente = usuario.adicionar_conta(ContaCorrente("Principal", limite=500))
        poupanca = usuario.adicionar_conta(ContaPoupanca("Reserva", taxa_rendimento=0.01))
        corrente.lancar(Receita(1000, HOJE, "Salário", SALARIO, fonte="Empresa"))
        corrente.lancar(Despesa(1200.5, HOJE, "Show", LAZER, "Cartão de crédito"))
        usuario.transferir(corrente, poupanca, 100, HOJE)
        self.repositorio.salvar(usuario)

        carregado = self.repositorio.carregar()
        self.assertEqual(carregado.nome, "Ana Souza")
        self.assertEqual([(c.nome, round(c.saldo, 2)) for c in carregado.contas],
                         [("Principal", -300.5), ("Reserva", 100)])
        self.assertEqual(carregado.contas[0].limite, 500)
        self.assertEqual(carregado.contas[1].taxa_rendimento, 0.01)
        self.assertEqual(len(carregado.lancamentos()), 4)

    def test_arquivo_nao_guarda_o_saldo(self):
        usuario = Usuario("Ana Souza", "ana@email.com")
        usuario.adicionar_conta(ContaCorrente("Principal"))
        self.repositorio.salvar(usuario)
        with open(self.repositorio.caminho_arquivo, encoding="utf-8") as arquivo:
            self.assertNotIn("saldo", arquivo.read())


if __name__ == "__main__":
    unittest.main()
