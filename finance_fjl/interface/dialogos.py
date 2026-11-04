"""Janelas de formulário: conta, lançamento e transferência."""
from abc import ABC, abstractmethod
from datetime import date
from tkinter import TclError

import customtkinter as ctk

from ..categoria import Categoria
from ..conta import ContaCorrente, ContaPoupanca
from ..excecoes import SaldoInsuficienteError
from ..formato import Formato
from ..transacao import Despesa, Receita
from .tema import Tema


class Dialogo(ctk.CTkToplevel, ABC):
    """Base dos formulários. Cada subclasse implementa montar() e salvar().

    Se salvar() lançar ValueError ou SaldoInsuficienteError, a mensagem aparece
    em vermelho no próprio formulário e a janela continua aberta.
    """

    def __init__(self, app, titulo):
        super().__init__(app, fg_color=Tema.FUNDO)
        self.app = app
        self.usuario = app.usuario
        self.title(titulo)
        self.resizable(False, False)
        self.transient(app)

        self.corpo = ctk.CTkFrame(self, fg_color="transparent")
        self.corpo.pack(fill="both", expand=True, padx=24, pady=20)
        ctk.CTkLabel(self.corpo, text=titulo, font=ctk.CTkFont(size=18, weight="bold"),
                     text_color=Tema.TEXTO, anchor="w").pack(fill="x", pady=(0, 6))
        self.campos = ctk.CTkFrame(self.corpo, fg_color="transparent")
        self.campos.pack(fill="x")
        self.erro = ctk.CTkLabel(self.corpo, text="", text_color=Tema.NEGATIVO, wraplength=340,
                                 justify="left", anchor="w")
        self.erro.pack(fill="x", pady=(8, 0))
        botoes = ctk.CTkFrame(self.corpo, fg_color="transparent")
        botoes.pack(fill="x", pady=(6, 0))
        ctk.CTkButton(botoes, text="Salvar", width=110, fg_color=Tema.VERDE,
                      hover_color=Tema.VERDE_ESCURO, command=self._confirmar).pack(side="right")
        ctk.CTkButton(botoes, text="Cancelar", width=90, fg_color="#8A94A0", hover_color="#737D89",
                      command=self.destroy).pack(side="right", padx=8)

        self.montar()
        self.after(60, self._exibir)

    @abstractmethod
    def montar(self):
        """Cria os campos do formulário."""

    @abstractmethod
    def salvar(self):
        """Aplica o formulário nas classes do sistema."""

    def _exibir(self):
        try:
            self.lift()
            self.focus_force()
            self.grab_set()
        except TclError:
            pass

    def _confirmar(self):
        try:
            self.salvar()
        except (ValueError, SaldoInsuficienteError) as erro:
            self.erro.configure(text=str(erro))
            return
        self.destroy()

    def campo_texto(self, rotulo, valor=""):
        ctk.CTkLabel(self.campos, text=rotulo, text_color=Tema.TEXTO_2, anchor="w").pack(fill="x")
        entrada = ctk.CTkEntry(self.campos, width=340)
        if valor:
            entrada.insert(0, valor)
        entrada.pack(fill="x", pady=(0, 6))
        return entrada

    def campo_opcoes(self, rotulo, opcoes, valor=None, comando=None):
        ctk.CTkLabel(self.campos, text=rotulo, text_color=Tema.TEXTO_2, anchor="w").pack(fill="x")
        menu = ctk.CTkOptionMenu(self.campos, values=list(opcoes), width=340, fg_color=Tema.VERDE,
                                 button_color=Tema.VERDE_ESCURO, command=comando)
        if valor:
            menu.set(valor)
        menu.pack(fill="x", pady=(0, 6))
        return menu


class DialogoConta(Dialogo):
    """Cria uma conta nova ou edita o nome e o limite/taxa de uma conta existente."""

    CORRENTE = "Conta corrente"
    POUPANCA = "Conta poupança"

    def __init__(self, app, conta=None):
        self.conta = conta
        super().__init__(app, "Editar conta" if conta else "Nova conta")

    def montar(self):
        self.tipo = None
        self.saldo_inicial = None
        if self.conta is None:
            self.tipo = self.campo_opcoes("Tipo", (self.CORRENTE, self.POUPANCA), self.CORRENTE,
                                          self._trocar_tipo)
            self.nome = self.campo_texto("Nome")
            self.rotulo_extra, self.extra = self._campo_extra("Limite do cheque especial (R$)", "0")
            self.saldo_inicial = self.campo_texto("Saldo inicial (R$)", "0")
        elif isinstance(self.conta, ContaCorrente):
            self.nome = self.campo_texto("Nome", self.conta.nome)
            self.rotulo_extra, self.extra = self._campo_extra("Limite do cheque especial (R$)",
                                                              str(self.conta.limite))
        else:
            self.nome = self.campo_texto("Nome", self.conta.nome)
            self.rotulo_extra, self.extra = self._campo_extra(
                "Rendimento ao mês (%)", str(round(self.conta.taxa_rendimento * 100, 4)))

    def _campo_extra(self, texto, valor):
        rotulo = ctk.CTkLabel(self.campos, text=texto, text_color=Tema.TEXTO_2, anchor="w")
        rotulo.pack(fill="x")
        entrada = ctk.CTkEntry(self.campos, width=340)
        entrada.insert(0, valor)
        entrada.pack(fill="x", pady=(0, 6))
        return rotulo, entrada

    def _trocar_tipo(self, tipo):
        poupanca = tipo == self.POUPANCA
        self.rotulo_extra.configure(text="Rendimento ao mês (%)" if poupanca
                                    else "Limite do cheque especial (R$)")
        self.extra.delete(0, "end")
        self.extra.insert(0, "0,5" if poupanca else "0")

    def salvar(self):
        if self.conta is None:
            extra = Formato.ler_valor(self.extra.get())
            saldo = Formato.ler_valor(self.saldo_inicial.get())
            if self.tipo.get() == self.POUPANCA:
                conta = ContaPoupanca(self.nome.get(), extra / 100)
            else:
                conta = ContaCorrente(self.nome.get(), extra)
            if saldo > 0:
                conta.lancar(Receita(saldo, date.today(), "Saldo inicial", Categoria.saldo_inicial()))
            self.usuario.adicionar_conta(conta)
        else:
            extra = Formato.ler_valor(self.extra.get())
            if isinstance(self.conta, ContaCorrente):
                self.conta.limite = extra
            else:
                self.conta.taxa_rendimento = extra / 100
            self.conta.nome = self.nome.get()
        self.app.registrar_alteracao()


class DialogoLancamento(Dialogo):
    """Lança uma receita ou uma despesa em uma conta."""

    def __init__(self, app, tipo):
        self.tipo_lancamento = tipo
        super().__init__(app, "Nova receita" if tipo == Receita.TIPO else "Nova despesa")

    def montar(self):
        categorias = [c.nome for c in self.usuario.categorias_do_tipo(self.tipo_lancamento)]
        contas = [c.nome for c in self.usuario.contas]
        self.valor = self.campo_texto("Valor (R$)")
        self.data = self.campo_texto("Data (DD/MM/AAAA)", Formato.data(date.today()))
        self.descricao = self.campo_texto("Descrição")
        self.categoria = self.campo_opcoes("Categoria", categorias)
        self.conta = self.campo_opcoes("Conta", contas)
        self.forma = None
        if self.tipo_lancamento == Despesa.TIPO:
            self.forma = self.campo_opcoes("Forma de pagamento", Despesa.FORMAS_PAGAMENTO[:-1])

    def salvar(self):
        valor = Formato.ler_valor(self.valor.get())
        data = Formato.ler_data(self.data.get())
        categoria = self.usuario.buscar_categoria(self.categoria.get(), self.tipo_lancamento)
        conta = self.usuario.buscar_conta(self.conta.get())
        if self.tipo_lancamento == Receita.TIPO:
            lancamento = Receita(valor, data, self.descricao.get(), categoria)
        else:
            lancamento = Despesa(valor, data, self.descricao.get(), categoria, self.forma.get())
        conta.lancar(lancamento)
        self.app.registrar_alteracao()


class DialogoTransferencia(Dialogo):
    """Transfere um valor entre duas contas do usuário."""

    def __init__(self, app):
        super().__init__(app, "Transferir entre contas")

    def montar(self):
        contas = [c.nome for c in self.usuario.contas]
        self.origem = self.campo_opcoes("Conta de origem", contas)
        self.destino = self.campo_opcoes("Conta de destino", contas)
        self.valor = self.campo_texto("Valor (R$)")

    def salvar(self):
        origem = self.usuario.buscar_conta(self.origem.get())
        destino = self.usuario.buscar_conta(self.destino.get())
        self.usuario.transferir(origem, destino, Formato.ler_valor(self.valor.get()))
        self.app.salvar()
