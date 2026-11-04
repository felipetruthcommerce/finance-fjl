"""Classe Repositorio: salva e carrega os dados do usuário em JSON."""
import json
import os
from datetime import date

from .categoria import Categoria
from .conta import ContaCorrente, ContaPoupanca
from .transacao import Despesa, Receita
from .usuario import Usuario


class Repositorio:
    """Guarda tudo em um arquivo JSON no computador do usuário."""

    VERSAO = 1

    def __init__(self, caminho_arquivo):
        self.caminho_arquivo = caminho_arquivo

    def existe(self):
        return os.path.exists(self.caminho_arquivo)

    def salvar(self, usuario):
        os.makedirs(os.path.dirname(os.path.abspath(self.caminho_arquivo)), exist_ok=True)
        with open(self.caminho_arquivo, "w", encoding="utf-8") as arquivo:
            json.dump(self.__serializar(usuario), arquivo, ensure_ascii=False, indent=2)

    def carregar(self):
        """Devolve o Usuario salvo, ou None se ainda não há dados (primeiro uso)."""
        if not self.existe():
            return None
        with open(self.caminho_arquivo, encoding="utf-8") as arquivo:
            return self.__desserializar(json.load(arquivo))

    def __serializar(self, usuario):                # método PRIVADO
        return {"versao": self.VERSAO,
                "usuario": {"nome": usuario.nome, "email": usuario.email},
                "contas": [conta.para_dict() for conta in usuario.contas]}

    def __desserializar(self, dados):               # método PRIVADO
        usuario = Usuario(dados["usuario"]["nome"], dados["usuario"]["email"])
        for dados_conta in dados["contas"]:
            if dados_conta["tipo"] == ContaCorrente.TIPO:
                conta = ContaCorrente(dados_conta["nome"], dados_conta["limite"])
            else:
                conta = ContaPoupanca(dados_conta["nome"], dados_conta["taxa_rendimento"])
            conta.restaurar_historico(self.__criar_transacao(t) for t in dados_conta["historico"])
            usuario.adicionar_conta(conta)
        return usuario

    def __criar_transacao(self, dados):             # método PRIVADO
        data = date.fromisoformat(dados["data"])
        categoria = Categoria(dados["categoria"], dados["tipo_categoria"])
        if dados["tipo"] == Receita.TIPO:
            return Receita(dados["valor"], data, dados["descricao"], categoria,
                           dados.get("fonte", ""), id_=dados["id"])
        return Despesa(dados["valor"], data, dados["descricao"], categoria,
                       dados.get("forma_pagamento", "Pix"), id_=dados["id"])
