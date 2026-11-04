"""Programa principal do Finance FJL.

Como usar:
    python main.py                 abre o sistema com os seus dados
    python main.py --demo          abre com dados de exemplo
    python main.py --demo --novo   gera os dados de exemplo de novo
"""
import os
import sys
from datetime import date

from finance_fjl import Categoria, ContaCorrente, ContaPoupanca, Receita, Repositorio, Usuario
from finance_fjl.demo import DadosDemonstracao
from finance_fjl.interface import AppFinanceFJL

PASTA_DADOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dados")


def criar_usuario(nome, email, saldo_inicial=0.0):
    """Primeiro acesso: cria o usuário com uma ContaCorrente e uma ContaPoupanca."""
    usuario = Usuario(nome, email)
    corrente = usuario.adicionar_conta(ContaCorrente("Conta corrente"))
    usuario.adicionar_conta(ContaPoupanca("Poupança"))
    if saldo_inicial > 0:
        corrente.lancar(Receita(saldo_inicial, date.today(), "Saldo inicial", Categoria.saldo_inicial()))
    return usuario


def main():
    demo = "--demo" in sys.argv
    repositorio = Repositorio(os.path.join(PASTA_DADOS, "demo.json" if demo else "finance_fjl.json"))
    if demo and ("--novo" in sys.argv or not repositorio.existe()):
        usuario = DadosDemonstracao().criar_usuario()
        repositorio.salvar(usuario)
    else:
        usuario = repositorio.carregar()     # None no primeiro uso
    AppFinanceFJL(usuario, repositorio, criar_usuario).mainloop()


if __name__ == "__main__":
    main()
