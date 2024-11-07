# cliente/simulador_erros.py
import random

def introduzir_erro(mensagem, probabilidade_erro=0.1):
    """
    Introduz um erro na mensagem com uma probabilidade especificada.
    """
    if random.random() < probabilidade_erro:
        # Introduz erro mudando um caractere aleatório na mensagem
        pos = random.randint(0, len(mensagem) - 1)
        mensagem = mensagem[:pos] + '?' + mensagem[pos + 1:]
    return mensagem

def simular_perda():
    """
    Retorna True para simular uma perda de pacote com uma certa probabilidade.
    """
    probabilidade_perda = 0.1
    return random.random() < probabilidade_perda
