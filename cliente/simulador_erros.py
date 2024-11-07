# cliente/simulador_erros.py
import random

def introduzir_erro(mensagem, probabilidade_erro=0.1):
    """
    Introduz um erro no conteúdo da mensagem, preservando o tipo e o número de sequência.
    """
    partes = mensagem.split(":")
    if len(partes) >= 2:
        tipo = partes[0]
        numero_sequencia = partes[1]

        # Introduz erro no conteúdo, se houver
        if len(partes) > 2:
            conteudo = partes[2]
            conteudo_com_erro = ''.join(random.choice('!@#$%?') if random.random() < probabilidade_erro else c for c in conteudo)
            partes[2] = conteudo_com_erro
        mensagem_com_erro = ":".join(partes)
    else:
        mensagem_com_erro = mensagem  # Retorna a mensagem sem alterações se o formato estiver incorreto
    
    return mensagem_com_erro

def simular_perda():
    """
    Retorna True para simular uma perda de pacote com uma certa probabilidade.
    """
    probabilidade_perda = 0.1
    return random.random() < probabilidade_perda
