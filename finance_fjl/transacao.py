"""Classes Transacao (abstrata), Receita e Despesa."""
import uuid
from abc import ABC, abstractmethod


class Transacao(ABC):
    """Base de todo lançamento financeiro.

    Classe abstrata: só existem Receita ou Despesa. Cada subclasse diz, em
    aplicar() e estornar(), o que acontece com a conta (polimorfismo).
    """

    TIPO = ""
    SINAL = 0

    def __init__(self, valor, data, descricao, categoria, id_=None):
        if not isinstance(valor, (int, float)) or valor <= 0:
            raise ValueError("O valor deve ser maior que zero.")
        descricao = str(descricao).strip()
        if not descricao:
            raise ValueError("Informe uma descrição.")
        self.valor = round(float(valor), 2)
        self.data = data
        self.descricao = descricao
        self.categoria = categoria
        self.id = id_ or uuid.uuid4().hex[:12]

    @abstractmethod
    def aplicar(self, conta):
        """Aplica o efeito deste lançamento no saldo da conta."""

    @abstractmethod
    def estornar(self, conta):
        """Desfaz o efeito deste lançamento (usado ao excluir)."""

    def valor_com_sinal(self):
        return self.SINAL * self.valor

    def no_mes(self, ano, mes):
        return self.data.year == ano and self.data.month == mes

    def para_dict(self):
        return {"tipo": self.TIPO, "id": self.id, "valor": self.valor,
                "data": self.data.isoformat(), "descricao": self.descricao,
                "categoria": self.categoria.nome, "tipo_categoria": self.categoria.tipo}


class Receita(Transacao):
    """Dinheiro que entra na conta."""

    TIPO = "receita"
    SINAL = 1

    def __init__(self, valor, data, descricao, categoria, fonte="", id_=None):
        super().__init__(valor, data, descricao, categoria, id_)
        self.fonte = str(fonte).strip()

    def aplicar(self, conta):
        conta.depositar(self.valor)

    def estornar(self, conta):
        conta.sacar(self.valor)

    def para_dict(self):
        dados = super().para_dict()
        dados["fonte"] = self.fonte
        return dados


class Despesa(Transacao):
    """Dinheiro que sai da conta."""

    TIPO = "despesa"
    SINAL = -1
    FORMAS_PAGAMENTO = ("Pix", "Cartão de débito", "Cartão de crédito", "Dinheiro", "Boleto",
                        "Transferência")

    def __init__(self, valor, data, descricao, categoria, forma_pagamento="Pix", id_=None):
        super().__init__(valor, data, descricao, categoria, id_)
        if forma_pagamento not in self.FORMAS_PAGAMENTO:
            raise ValueError("Forma de pagamento inválida.")
        self.forma_pagamento = forma_pagamento

    def aplicar(self, conta):
        conta.sacar(self.valor)

    def estornar(self, conta):
        conta.depositar(self.valor)

    def para_dict(self):
        dados = super().para_dict()
        dados["forma_pagamento"] = self.forma_pagamento
        return dados
