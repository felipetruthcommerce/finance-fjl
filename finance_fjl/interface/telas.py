"""Telas do menu: Início, Contas e Lançamentos, além do cadastro de primeiro acesso."""
from abc import ABC, abstractmethod
from datetime import date
from tkinter import messagebox, ttk

import customtkinter as ctk

from ..conta import ContaCorrente, ContaPoupanca
from ..excecoes import SaldoInsuficienteError
from ..formato import Formato
from ..transacao import Despesa, Receita
from .dialogos import DialogoConta, DialogoLancamento, DialogoTransferencia
from .tema import Tema


def rotulo(master, texto, tamanho=13, negrito=False, cor=Tema.TEXTO, **opcoes):
    fonte = ctk.CTkFont(size=tamanho, weight="bold" if negrito else "normal")
    return ctk.CTkLabel(master, text=texto, font=fonte, text_color=cor, anchor="w", **opcoes)


class TelaCadastro(ctk.CTkFrame):
    """Aparece só no primeiro acesso, quando ainda não há dados salvos."""

    def __init__(self, app, ao_concluir):
        super().__init__(app, fg_color=Tema.FUNDO, corner_radius=0)
        self.ao_concluir = ao_concluir
        cartao = ctk.CTkFrame(self, fg_color=Tema.CARTAO, corner_radius=10)
        cartao.place(relx=0.5, rely=0.5, anchor="center")
        miolo = ctk.CTkFrame(cartao, fg_color="transparent")
        miolo.pack(padx=32, pady=26)

        rotulo(miolo, "Finance FJL", 24, True, Tema.AZUL_MARINHO).pack(fill="x")
        rotulo(miolo, "Primeiro acesso: criaremos uma conta corrente e uma poupança.",
               12, cor=Tema.TEXTO_2).pack(fill="x", pady=(0, 12))
        self.nome = self._campo(miolo, "Nome")
        self.email = self._campo(miolo, "E-mail")
        self.saldo = self._campo(miolo, "Saldo atual da conta corrente (opcional)")
        self.erro = rotulo(miolo, "", 12, cor=Tema.NEGATIVO, wraplength=360)
        self.erro.pack(fill="x")
        ctk.CTkButton(miolo, text="Começar", fg_color=Tema.VERDE, hover_color=Tema.VERDE_ESCURO,
                      command=self._concluir).pack(fill="x", pady=(6, 0))

    def _campo(self, master, texto):
        rotulo(master, texto, 12, cor=Tema.TEXTO_2).pack(fill="x")
        entrada = ctk.CTkEntry(master, width=360)
        entrada.pack(fill="x", pady=(0, 8))
        return entrada

    def _concluir(self):
        try:
            texto = self.saldo.get().strip()
            self.ao_concluir(self.nome.get(), self.email.get(), Formato.ler_valor(texto) if texto else 0.0)
        except ValueError as erro:
            self.erro.configure(text=str(erro))


class Tela(ctk.CTkFrame, ABC):
    """Toda tela tem título, botões de ação e corpo.

    A janela chama atualizar() sem precisar saber qual tela é (polimorfismo).
    """

    TITULO = ""

    def __init__(self, app):
        super().__init__(app.conteudo, fg_color="transparent")
        self.app = app
        cabecalho = ctk.CTkFrame(self, fg_color="transparent")
        cabecalho.pack(fill="x", padx=24, pady=(20, 10))
        self.titulo = rotulo(cabecalho, self.TITULO, 22, True)
        self.titulo.pack(side="left")
        self.acoes = ctk.CTkFrame(cabecalho, fg_color="transparent", height=1)
        self.acoes.pack(side="right")
        self.corpo = ctk.CTkFrame(self, fg_color="transparent")
        self.corpo.pack(fill="both", expand=True, padx=24, pady=(0, 18))
        self.montar()

    @property
    def usuario(self):
        return self.app.usuario

    def botao(self, texto, comando, secundario=False):
        cor, hover = ("#8A94A0", "#737D89") if secundario else (Tema.VERDE, Tema.VERDE_ESCURO)
        ctk.CTkButton(self.acoes, text=texto, width=110, fg_color=cor, hover_color=hover,
                      command=comando).pack(side="left", padx=(8, 0))

    def limpar(self):
        for filho in self.corpo.winfo_children():
            filho.destroy()

    @abstractmethod
    def montar(self):
        """Cria os elementos fixos da tela."""

    @abstractmethod
    def atualizar(self):
        """Mostra os dados atuais do usuário."""


class TelaInicio(Tela):
    """Resumo: saldo total, receitas e despesas do mês, contas e últimos lançamentos."""

    TITULO = "Início"

    def montar(self):
        pass

    def atualizar(self):
        self.limpar()
        self.titulo.configure(text="Olá, {}!".format(self.usuario.primeiro_nome))
        hoje = date.today()
        resumo = self.usuario.resumo_mes(hoje.year, hoje.month)

        linha = ctk.CTkFrame(self.corpo, fg_color="transparent")
        linha.pack(fill="x")
        indicadores = [("Saldo total", self.usuario.saldo_total(), Tema.TEXTO),
                       ("Receitas do mês", resumo["receitas"], Tema.POSITIVO),
                       ("Despesas do mês", resumo["despesas"], Tema.NEGATIVO)]
        for coluna, (titulo, valor, cor) in enumerate(indicadores):
            linha.grid_columnconfigure(coluna, weight=1, uniform="ind")
            cartao = ctk.CTkFrame(linha, fg_color=Tema.CARTAO, corner_radius=8)
            cartao.grid(row=0, column=coluna, sticky="ew", padx=(0 if coluna == 0 else 10, 0))
            rotulo(cartao, titulo, 12, cor=Tema.TEXTO_2).pack(fill="x", padx=14, pady=(10, 0))
            rotulo(cartao, Formato.moeda(valor), 20, True, cor).pack(fill="x", padx=14, pady=(0, 10))

        contas = ctk.CTkFrame(self.corpo, fg_color=Tema.CARTAO, corner_radius=8)
        contas.pack(fill="x", pady=(12, 0))
        rotulo(contas, "Minhas contas", 14, True).pack(fill="x", padx=14, pady=(10, 4))
        for conta in self.usuario.contas:
            item = ctk.CTkFrame(contas, fg_color="transparent")
            item.pack(fill="x", padx=14)
            rotulo(item, "{}  ({})".format(conta.nome, conta.descricao_tipo())).pack(side="left")
            rotulo(item, Formato.moeda(conta.saldo), negrito=True).pack(side="right")
        ctk.CTkFrame(contas, fg_color="transparent", height=8).pack()

        ultimos = ctk.CTkFrame(self.corpo, fg_color=Tema.CARTAO, corner_radius=8)
        ultimos.pack(fill="both", expand=True, pady=(12, 0))
        rotulo(ultimos, "Últimos lançamentos", 14, True).pack(fill="x", padx=14, pady=(10, 4))
        for conta, transacao in self.usuario.lancamentos()[:6]:
            item = ctk.CTkFrame(ultimos, fg_color="transparent")
            item.pack(fill="x", padx=14)
            rotulo(item, "{}   {}  ({})".format(Formato.data(transacao.data), transacao.descricao,
                                                conta.nome)).pack(side="left")
            cor = Tema.POSITIVO if transacao.SINAL > 0 else Tema.NEGATIVO
            rotulo(item, Formato.moeda(transacao.valor_com_sinal()), cor=cor).pack(side="right")


class TelaContas(Tela):
    """Lista as contas, com as ações de cada uma."""

    TITULO = "Contas"

    def montar(self):
        self.botao("Transferir", self._transferir, secundario=True)
        self.botao("Nova conta", lambda: DialogoConta(self.app))

    def atualizar(self):
        self.limpar()
        for conta in self.usuario.contas:
            cartao = ctk.CTkFrame(self.corpo, fg_color=Tema.CARTAO, corner_radius=8)
            cartao.pack(fill="x", pady=(0, 10))
            textos = ctk.CTkFrame(cartao, fg_color="transparent")
            textos.pack(side="left", padx=14, pady=10)
            rotulo(textos, conta.nome, 15, True).pack(fill="x")
            rotulo(textos, self._detalhe(conta), 12, cor=Tema.TEXTO_2).pack(fill="x")
            rotulo(textos, Formato.moeda(conta.saldo), 18, True,
                   Tema.NEGATIVO if conta.saldo < 0 else Tema.TEXTO).pack(fill="x")
            acoes = ctk.CTkFrame(cartao, fg_color="transparent")
            acoes.pack(side="right", padx=14)
            if isinstance(conta, ContaPoupanca):
                self._acao(acoes, "Render", lambda c=conta: self._render(c))
            self._acao(acoes, "Editar", lambda c=conta: DialogoConta(self.app, c))
            self._acao(acoes, "Excluir", lambda c=conta: self._excluir(c))

    @staticmethod
    def _acao(master, texto, comando):
        ctk.CTkButton(master, text=texto, width=78, fg_color="#8A94A0", hover_color="#737D89",
                      command=comando).pack(side="left", padx=(6, 0))

    @staticmethod
    def _detalhe(conta):
        if isinstance(conta, ContaCorrente):
            return "{}  ·  limite de {}".format(conta.descricao_tipo(), Formato.moeda(conta.limite))
        return "{}  ·  rende {:.2f}% ao mês".format(conta.descricao_tipo(),
                                                    conta.taxa_rendimento * 100).replace(".", ",")

    def _transferir(self):
        DialogoTransferencia(self.app)

    def _render(self, conta):
        try:
            conta.render()
        except ValueError as erro:
            messagebox.showerror("Finance FJL", str(erro), parent=self.app)
            return
        self.app.registrar_alteracao()

    def _excluir(self, conta):
        if not messagebox.askyesno("Finance FJL", "Excluir a conta {}?".format(conta.nome),
                                   parent=self.app):
            return
        try:
            self.usuario.remover_conta(conta)
        except ValueError as erro:
            messagebox.showerror("Finance FJL", str(erro), parent=self.app)
            return
        self.app.registrar_alteracao()


class TelaLancamentos(Tela):
    """Extrato com todos os lançamentos, do mais recente para o mais antigo."""

    TITULO = "Lançamentos"
    COLUNAS = (("data", "Data", 90, "w"), ("descricao", "Descrição", 240, "w"),
               ("categoria", "Categoria", 140, "w"), ("conta", "Conta", 130, "w"),
               ("valor", "Valor", 110, "e"))

    def montar(self):
        self.botao("Excluir", self._excluir, secundario=True)
        self.botao("+ Despesa", lambda: DialogoLancamento(self.app, Despesa.TIPO))
        self.botao("+ Receita", lambda: DialogoLancamento(self.app, Receita.TIPO))

        estilo = ttk.Style()
        estilo.theme_use("clam")
        estilo.configure("Treeview", rowheight=26, background=Tema.CARTAO, fieldbackground=Tema.CARTAO,
                         foreground=Tema.TEXTO)
        estilo.map("Treeview", background=[("selected", "#CDEFE0")], foreground=[("selected", Tema.TEXTO)])
        self.tabela = ttk.Treeview(self.corpo, columns=[c[0] for c in self.COLUNAS], show="headings",
                                   selectmode="browse")
        for chave, titulo, largura, alinhamento in self.COLUNAS:
            self.tabela.heading(chave, text=titulo, anchor=alinhamento)
            self.tabela.column(chave, width=largura, anchor=alinhamento)
        rolagem = ttk.Scrollbar(self.corpo, command=self.tabela.yview)
        self.tabela.configure(yscrollcommand=rolagem.set)
        self.tabela.pack(side="left", fill="both", expand=True)
        rolagem.pack(side="right", fill="y")
        self.linhas = {}

    def atualizar(self):
        self.tabela.delete(*self.tabela.get_children())
        self.linhas = {}
        for conta, transacao in self.usuario.lancamentos():
            self.linhas[transacao.id] = (conta, transacao)
            self.tabela.insert("", "end", iid=transacao.id, values=(
                Formato.data(transacao.data), transacao.descricao, transacao.categoria.nome,
                conta.nome, Formato.moeda(transacao.valor_com_sinal())))

    def _excluir(self):
        selecionados = self.tabela.selection()
        if not selecionados:
            messagebox.showinfo("Finance FJL", "Selecione um lançamento na tabela.", parent=self.app)
            return
        conta, transacao = self.linhas[selecionados[0]]
        if not messagebox.askyesno("Finance FJL", "Excluir \"{}\"?".format(transacao.descricao),
                                   parent=self.app):
            return
        try:
            self.usuario.excluir_lancamento(conta, transacao)
        except SaldoInsuficienteError as erro:
            messagebox.showerror("Finance FJL", str(erro), parent=self.app)
            return
        self.app.registrar_alteracao()
