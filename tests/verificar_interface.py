"""Verificação da interface: abre a janela e simula os fluxos principais.

Como rodar (a janela abre por alguns segundos e fecha sozinha):
    python -m tests.verificar_interface
"""
import os
import sys
import tempfile
import traceback
from unittest import mock

import main as programa
from finance_fjl import ContaPoupanca, Formato, Repositorio
from finance_fjl.demo import DadosDemonstracao
from finance_fjl.interface import AppFinanceFJL, dialogos, telas


class VerificacaoInterface:
    """Preenche os formulários como um usuário faria e confere o resultado nas classes."""

    def __init__(self):
        self.repositorio = Repositorio(os.path.join(tempfile.mkdtemp(), "verificacao.json"))
        self.usuario = DadosDemonstracao().criar_usuario()
        self.app = AppFinanceFJL(self.usuario, self.repositorio, programa.criar_usuario)
        self.total = 0
        self.falhas = []
        self.bugs_confirmados = []

    def checar(self, condicao, mensagem):
        self.total += 1
        print(("OK     " if condicao else "FALHA  ") + mensagem, flush=True)
        if not condicao:
            self.falhas.append(mensagem)

    def bug(self, confirmado, mensagem):
        print(("BUG    " if confirmado else "MUDOU  ") + mensagem, flush=True)
        if confirmado:
            self.bugs_confirmados.append(mensagem)

    def formulario(self, classe, campos, *args):
        """Abre o formulário, preenche, confirma e devolve a mensagem de erro (se houver)."""
        janela = classe(self.app, *args)
        for nome, valor in campos.items():
            campo = getattr(janela, nome)
            if hasattr(campo, "insert") and not hasattr(campo, "set"):
                campo.delete(0, "end")
                campo.insert(0, valor)
            else:
                campo.set(valor)
        janela._confirmar()
        erro = janela.erro.cget("text") if janela.winfo_exists() else ""
        if janela.winfo_exists():
            janela.destroy()
        return erro

    def executar(self):
        try:
            with mock.patch.object(telas.messagebox, "askyesno", return_value=True), \
                 mock.patch.object(telas.messagebox, "showerror") as self.janela_de_erro:
                self.fluxos()
        except Exception:
            traceback.print_exc()
            self.falhas.append("exceção inesperada")
        print("\n{} verificações, {} falha(s); {} bug(s) conhecido(s) confirmado(s)".format(
            self.total, len(self.falhas), len(self.bugs_confirmados)))
        self.app.destroy()

    def fluxos(self):
        u, checar, form = self.usuario, self.checar, self.formulario
        principal, poupanca, carteira = u.contas
        dlg = dialogos

        for chave, _titulo, _classe in AppFinanceFJL.MENU:
            self.app.mostrar(chave)
        checar(True, "as três telas abrem")

        antes = principal.saldo
        erro = form(dlg.DialogoLancamento, {"valor": "100,50", "descricao": "Teste", "categoria": "Compras"},
                    "despesa")
        checar(erro == "" and round(antes - principal.saldo, 2) == 100.5, "despesa lançada pelo formulário")
        checar(round(self.repositorio.carregar().contas[0].saldo, 2) == round(principal.saldo, 2),
               "salvou automaticamente no JSON")
        antes = principal.saldo
        erro = form(dlg.DialogoLancamento, {"valor": "250", "descricao": "Freela", "categoria": "Freelance"},
                    "receita")
        checar(erro == "" and round(principal.saldo - antes, 2) == 250, "receita lançada pelo formulário")
        erro = form(dlg.DialogoLancamento, {"valor": "-5", "descricao": "X"}, "despesa")
        checar("maior que zero" in erro, "valor negativo recusado")
        erro = form(dlg.DialogoLancamento, {"valor": "10", "descricao": ""}, "receita")
        checar("descrição" in erro, "descrição vazia recusada")

        erro = form(dlg.DialogoTransferencia, {"valor": "99999", "origem": "Carteira", "destino": "Poupança"})
        checar("Saldo insuficiente" in erro, "transferência sem saldo recusada")
        erro = form(dlg.DialogoTransferencia, {"valor": "50", "origem": "Carteira", "destino": "Carteira"})
        checar("diferente" in erro, "transferência para a mesma conta recusada")
        antes = carteira.saldo
        erro = form(dlg.DialogoTransferencia, {"valor": "50", "origem": "Carteira", "destino": "Poupança"})
        checar(erro == "" and round(antes - carteira.saldo, 2) == 50, "transferência feita")

        erro = form(dlg.DialogoConta, {"nome": "Investimentos", "extra": "0", "saldo_inicial": "1000"})
        checar(erro == "" and u.buscar_conta("Investimentos").saldo == 1000, "conta corrente criada")
        janela = dlg.DialogoConta(self.app)
        janela.tipo.set(janela.POUPANCA)
        janela._trocar_tipo(janela.POUPANCA)
        janela.nome.insert(0, "Reserva 2")
        janela._confirmar()
        checar(isinstance(u.buscar_conta("Reserva 2"), ContaPoupanca), "conta poupança criada")
        erro = form(dlg.DialogoConta, {"nome": "Banco", "extra": "1500"}, principal)
        checar(principal.nome == "Banco" and principal.limite == 1500, "conta editada")

        self.app.mostrar("contas")
        tela = self.app.telas["contas"]
        tela._excluir(u.buscar_conta("Reserva 2"))
        checar(u.buscar_conta("Reserva 2") is None, "conta excluída")
        antes = poupanca.saldo
        tela._render(poupanca)
        checar(poupanca.saldo > antes, "rendimento aplicado")

        self.app.mostrar("lancamentos")
        lancamentos = self.app.telas["lancamentos"]
        conta, primeira = u.lancamentos()[0]
        lancamentos.tabela.selection_set(primeira.id)
        quantidade = len(u.lancamentos())
        lancamentos._excluir()
        checar(len(u.lancamentos()) == quantidade - 1, "lançamento excluído pela tabela")
        checar(len(lancamentos.tabela.get_children()) == quantidade - 1, "tabela atualizada depois de excluir")

        recarregado = self.repositorio.carregar()
        checar([(c.nome, round(c.saldo, 2)) for c in recarregado.contas]
               == [(c.nome, round(c.saldo, 2)) for c in u.contas], "arquivo salvo confere com a tela")

        # B8: depois de transferir, a tela de Contas continua mostrando o saldo antigo
        self.app.mostrar("contas")
        self.app.update()
        destino = u.buscar_conta("Carteira")
        origem = u.buscar_conta("Poupança")
        form(dlg.DialogoTransferencia, {"valor": "10", "origem": origem.nome, "destino": destino.nome})
        self.app.update()
        textos = [w.cget("text") for w in self._rotulos(self.app.telas["contas"].corpo)]
        self.bug(Formato.moeda(destino.saldo) not in textos,
                 "B8: tela de Contas não atualiza depois da transferência")

        # B11: ao editar uma conta com o nome vazio, o erro aparece, mas o limite já mudou
        limite = principal.limite
        erro = form(dlg.DialogoConta, {"nome": "", "extra": str(limite + 100)}, principal)
        self.bug("nome da conta" in erro and principal.limite != limite,
                 "B11: editar conta com nome vazio mostra o erro, mas altera o limite")

    def _rotulos(self, widget):
        for filho in widget.winfo_children():
            if type(filho).__name__ == "CTkLabel":
                yield filho
            yield from self._rotulos(filho)


if __name__ == "__main__":
    verificacao = VerificacaoInterface()
    verificacao.app.after(600, verificacao.executar)
    verificacao.app.mainloop()
    sys.exit(1 if verificacao.falhas else 0)
