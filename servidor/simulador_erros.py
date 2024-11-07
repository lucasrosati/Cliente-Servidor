# servidor/simulador_erros.py
import random

def introduzir_erro_ack(ack, probabilidade_erro=0.1):
    """
    Introduz um erro no conteúdo do ACK/NAK, preservando o tipo da mensagem e o número de sequência.
    """
    partes = ack.split(":")
    if len(partes) >= 2:
        # Preserva o tipo (ACK/NAK) e número de sequência
        tipo = partes[0]
        numero_sequencia = partes[1]

        # Introduz erro no conteúdo, se houver
        if len(partes) > 2:
            conteudo = partes[2]
            conteudo_com_erro = ''.join(random.choice('!@#$%?') if random.random() < probabilidade_erro else c for c in conteudo)
            partes[2] = conteudo_com_erro
        ack_com_erro = ":".join(partes)
    else:
        ack_com_erro = ack  # Retorna a mensagem sem alterações se o formato estiver incorreto
    
    return ack_com_erro

def simular_perda_ack():
    """
    Retorna True para simular a perda de um ACK.
    """
    probabilidade_perda_ack = 0.1
    return random.random() < probabilidade_perda_ack
