"""Conversão de valores e datas entre o formato brasileiro e o Python."""
import math
from datetime import datetime


class Formato:
    """Métodos estáticos usados pelas telas e pelas mensagens de erro."""

    @staticmethod
    def moeda(valor):
        """1234.5 -> 'R$ 1.234,50'."""
        texto = "{:,.2f}".format(abs(valor))
        texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
        return ("-R$ " if valor < 0 else "R$ ") + texto

    @staticmethod
    def data(dia):
        """date(2026, 11, 5) -> '05/11/2026'."""
        return dia.strftime("%d/%m/%Y")

    @staticmethod
    def ler_valor(texto):
        """Troca a vírgula por ponto e converte para float: '150,90' -> 150.9."""
        valor = float(str(texto).strip().replace(",", "."))
        if not math.isfinite(valor):
            raise ValueError("Valor inválido.")
        return valor

    @staticmethod
    def ler_data(texto):
        """'05/11/2026' -> date(2026, 11, 5)."""
        return datetime.strptime(str(texto).strip(), "%d/%m/%Y").date()
