"""Classe Categoria: classifica receitas e despesas."""


class Categoria:
    """Classificação de um lançamento (Alimentação, Salário, Lazer...).

    Nesta versão as categorias são fixas: o usuário ainda não cria as suas.
    """

    RECEITA = "receita"
    DESPESA = "despesa"
    SISTEMA = "sistema"     # transferência e saldo inicial

    def __init__(self, nome, tipo):
        nome = str(nome).strip()
        if not nome:
            raise ValueError("Informe o nome da categoria.")
        if tipo not in (self.RECEITA, self.DESPESA, self.SISTEMA):
            raise ValueError("Tipo de categoria inválido: {}.".format(tipo))
        self.nome = nome
        self.tipo = tipo

    def __eq__(self, outra):
        if not isinstance(outra, Categoria):
            return NotImplemented
        return (self.nome.lower(), self.tipo) == (outra.nome.lower(), outra.tipo)

    def __hash__(self):
        return hash((self.nome.lower(), self.tipo))

    def __str__(self):
        return self.nome

    @classmethod
    def transferencia(cls):
        return cls("Transferência", cls.SISTEMA)

    @classmethod
    def saldo_inicial(cls):
        return cls("Saldo inicial", cls.SISTEMA)

    @classmethod
    def rendimentos(cls):
        return cls("Rendimentos", cls.RECEITA)

    @classmethod
    def padroes(cls):
        """Categorias de todo usuário."""
        despesas = ["Moradia", "Alimentação", "Transporte", "Lazer", "Compras",
                    "Contas e serviços", "Educação", "Saúde", "Outras despesas"]
        receitas = ["Salário", "Freelance", "Outras receitas"]
        return ([cls(n, cls.DESPESA) for n in despesas]
                + [cls(n, cls.RECEITA) for n in receitas]
                + [cls.rendimentos(), cls.transferencia(), cls.saldo_inicial()])
