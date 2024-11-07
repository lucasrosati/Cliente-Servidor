# servidor/simulador_erros.py
import random

def introduzir_erro_ack(ack, probabilidade_erro=0.1):
    """
    Introduz um erro na mensagem de ACK com uma probabilidade especificada.
    """
    if random.random() < probabilidade_erro:
        # Introduz erro mudando um caractere aleatório no ACK
        pos = random.randint(0, len(ack) - 1)
        ack = ack[:pos] + '?' + ack[pos + 1:]
    return ack

def simular_perda_ack():
    """
    Retorna True para simular a perda de um ACK.
    """
    probabilidade_perda_ack = 0.1
    return random.random() < probabilidade_perda_ack
