"""Classes Conta (abstrata), ContaCorrente e ContaPoupanca.

Diferencial do projeto: o saldo é um atributo privado (__saldo). Ele só muda
por depositar() e sacar(), que validam o valor antes. Para ler o saldo existe
a propriedade somente leitura `saldo`; `conta.saldo = 1000` gera erro.
"""
from abc import ABC, abstractmethod
from datetime import date

from .categoria import Categoria
from .excecoes import SaldoInsuficienteError
from .formato import Formato
from .transacao import Despesa, Receita


class Conta(ABC):
    """Base de toda conta: guarda o saldo protegido e o histórico."""

    TIPO = ""

    def __init__(self, nome):
        self.nome = nome
        self.__saldo = 0.0          # atributo PRIVADO
        self.__historico = []       # lançamentos desta conta (composição)

    @property
    def nome(self):
        return self._nome

    @nome.setter
    def nome(self, valor):
        valor = str(valor).strip()
        if not valor:
            raise ValueError("Informe o nome da conta.")
        self._nome = valor

    @property
    def saldo(self):
        """Leitura do saldo. Não há setter: o saldo é somente leitura."""
        return self.__saldo

    @property
    def historico(self):
        return tuple(self.__historico)

    @abstractmethod
    def descricao_tipo(self):
        """Nome do tipo de conta mostrado na tela."""

    def depositar(self, valor):
        self.__validar_valor(valor)
        self.__saldo += valor

    def sacar(self, valor):
        self.__validar_valor(valor)
        if valor > self.disponivel_para_saque():     # polimorfismo
            raise SaldoInsuficienteError(valor, self.disponivel_para_saque())
        self.__saldo -= valor

    def disponivel_para_saque(self):
        """Quanto ainda pode sair da conta. A ContaCorrente soma o limite."""
        return self.__saldo

    def lancar(self, transacao):
        """Registra uma Receita ou Despesa: a conta chama aplicar() sem saber o tipo."""
        transacao.aplicar(self)
        self.__historico.append(transacao)
        return transacao

    def remover_lancamento(self, transacao):
        """Exclui um lançamento desfazendo o seu efeito no saldo."""
        transacao.estornar(self)
        self.__historico.remove(transacao)

    def transferir(self, valor, destino, data=None):
        """Gera uma Despesa nesta conta e uma Receita na conta de destino."""
        if destino is self:
            raise ValueError("Escolha uma conta de destino diferente da origem.")
        data = data or date.today()
        categoria = Categoria.transferencia()
        saida = Despesa(valor, data, "Transferência para " + destino.nome, categoria,
                        forma_pagamento="Transferência")
        entrada = Receita(valor, data, "Transferência de " + self.nome, categoria)
        self.lancar(saida)        # se faltar saldo, para aqui e nada muda no destino
        destino.lancar(entrada)
        return saida, entrada

    def restaurar_historico(self, transacoes):
        """Usado pelo Repositorio: o saldo é recalculado a partir dos lançamentos."""
        transacoes = list(transacoes)
        total = round(sum(t.valor_com_sinal() for t in transacoes), 2)
        if total > 0:
            self.depositar(total)
        elif total < 0:
            self.sacar(-total)
        self.__historico.extend(transacoes)

    def __validar_valor(self, valor):                # método PRIVADO
        if not isinstance(valor, (int, float)) or isinstance(valor, bool):
            raise ValueError("O valor deve ser um número.")
        if valor <= 0:
            raise ValueError("O valor deve ser maior que zero.")

    def para_dict(self):
        return {"tipo": self.TIPO, "nome": self.nome,
                "historico": [t.para_dict() for t in self.__historico]}


class ContaCorrente(Conta):
    """Conta do dia a dia, com limite de cheque especial."""

    TIPO = "corrente"

    def __init__(self, nome, limite=0.0):
        super().__init__(nome)
        self.limite = limite

    @property
    def limite(self):
        return self._limite

    @limite.setter
    def limite(self, valor):
        if not isinstance(valor, (int, float)) or valor < 0:
            raise ValueError("O limite não pode ser negativo.")
        if self.saldo < 0 and valor < -self.saldo:
            raise ValueError("O limite não pode ser menor que o valor já usado ({})."
                             .format(Formato.moeda(-self.saldo)))
        self._limite = float(valor)

    def disponivel_para_saque(self):                # sobrescrito: soma o limite
        return self.saldo + self.limite

    def descricao_tipo(self):
        return "Conta corrente"

    def para_dict(self):
        dados = super().para_dict()
        dados["limite"] = self.limite
        return dados


class ContaPoupanca(Conta):
    """Conta para guardar dinheiro: rende juros e nunca fica negativa."""

    TIPO = "poupanca"

    def __init__(self, nome, taxa_rendimento=0.005):
        super().__init__(nome)
        self.taxa_rendimento = taxa_rendimento

    @property
    def taxa_rendimento(self):
        return self._taxa_rendimento

    @taxa_rendimento.setter
    def taxa_rendimento(self, valor):
        if not isinstance(valor, (int, float)) or not 0 <= valor <= 0.1:
            raise ValueError("A taxa de rendimento deve ficar entre 0% e 10% ao mês.")
        self._taxa_rendimento = float(valor)

    def rendimento_previsto(self):
        return round(max(self.saldo, 0.0) * self.taxa_rendimento, 2)

    def render(self, data=None):
        """Aplica o rendimento. O dinheiro entra por depositar()."""
        valor = self.rendimento_previsto()
        if valor <= 0:
            raise ValueError("Não há saldo para render nesta poupança.")
        receita = Receita(valor, data or date.today(), "Rendimento da poupança",
                          Categoria.rendimentos(), fonte=self.nome)
        return self.lancar(receita)

    def descricao_tipo(self):
        return "Conta poupança"

    def para_dict(self):
        dados = super().para_dict()
        dados["taxa_rendimento"] = self.taxa_rendimento
        return dados
