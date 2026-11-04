"""Classe AppFinanceFJL: a janela principal do sistema."""
import customtkinter as ctk

from .. import __version__
from .telas import TelaCadastro, TelaContas, TelaInicio, TelaLancamentos
from .tema import Tema


class AppFinanceFJL(ctk.CTk):
    """Janela com menu lateral. Salva automaticamente depois de cada alteração."""

    MENU = (("inicio", "Início", TelaInicio),
            ("contas", "Contas", TelaContas),
            ("lancamentos", "Lançamentos", TelaLancamentos))
    EM_DESENVOLVIMENTO = ("Orçamentos", "Metas", "Relatórios")

    def __init__(self, usuario, repositorio, criar_usuario=None):
        ctk.set_appearance_mode("light")
        super().__init__(fg_color=Tema.FUNDO)
        self.usuario = usuario
        self.repositorio = repositorio
        self.criar_usuario = criar_usuario
        self.telas = {}
        self.tela_atual = None
        self.botoes_menu = {}

        self.title("Finance FJL")
        self.geometry("1000x640")
        self.minsize(900, 580)

        if usuario is None:
            self.cadastro = TelaCadastro(self, self._concluir_cadastro)
            self.cadastro.pack(fill="both", expand=True)
        else:
            self._montar()

    def _montar(self):
        self.menu = ctk.CTkFrame(self, width=190, corner_radius=0, fg_color=Tema.AZUL_MARINHO)
        self.menu.pack(side="left", fill="y")
        self.menu.pack_propagate(False)
        self.conteudo = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        self.conteudo.pack(side="left", fill="both", expand=True)

        ctk.CTkLabel(self.menu, text="Finance FJL", text_color="#FFFFFF",
                     font=ctk.CTkFont(size=20, weight="bold")).pack(padx=16, pady=(22, 18), anchor="w")
        for chave, titulo, _classe in self.MENU:
            botao = ctk.CTkButton(self.menu, text=titulo, anchor="w", corner_radius=6,
                                  fg_color="transparent", hover_color=Tema.AZUL_HOVER,
                                  text_color=Tema.MENU_TEXTO, command=lambda c=chave: self.mostrar(c))
            botao.pack(fill="x", padx=10, pady=2)
            self.botoes_menu[chave] = botao
        for titulo in self.EM_DESENVOLVIMENTO:
            ctk.CTkButton(self.menu, text=titulo + " (em breve)", anchor="w", corner_radius=6,
                          fg_color="transparent", state="disabled",
                          text_color_disabled=Tema.MENU_INATIVO).pack(fill="x", padx=10, pady=2)

        ctk.CTkLabel(self.menu, text="versão " + __version__, text_color=Tema.MENU_INATIVO,
                     font=ctk.CTkFont(size=11)).pack(side="bottom", padx=16, pady=(0, 12), anchor="w")
        ctk.CTkLabel(self.menu, text=self.usuario.nome, text_color="#FFFFFF",
                     font=ctk.CTkFont(size=13, weight="bold")).pack(side="bottom", padx=16, anchor="w")
        self.mostrar("inicio")

    def _concluir_cadastro(self, nome, email, saldo_inicial):
        self.usuario = self.criar_usuario(nome, email, saldo_inicial)
        self.cadastro.destroy()
        self.salvar()
        self._montar()

    def mostrar(self, chave):
        """Troca a tela visível. Cada tela é criada só na primeira vez."""
        if self.tela_atual is not None:
            self.tela_atual.pack_forget()
        if chave not in self.telas:
            classe = next(c for k, _t, c in self.MENU if k == chave)
            self.telas[chave] = classe(self)
        self.tela_atual = self.telas[chave]
        self.tela_atual.pack(fill="both", expand=True)
        self.tela_atual.atualizar()                     # polimorfismo: cada tela se atualiza
        for k, botao in self.botoes_menu.items():
            ativo = k == chave
            botao.configure(fg_color=Tema.VERDE if ativo else "transparent",
                            hover_color=Tema.VERDE_ESCURO if ativo else Tema.AZUL_HOVER,
                            text_color="#FFFFFF" if ativo else Tema.MENU_TEXTO)

    def salvar(self):
        self.repositorio.salvar(self.usuario)

    def registrar_alteracao(self):
        """Chamado depois de uma alteração: salva e atualiza a tela aberta."""
        self.salvar()
        if self.tela_atual is not None:
            self.tela_atual.atualizar()
