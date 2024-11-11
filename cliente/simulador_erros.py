# cliente/simulador_erros.py
import random

def introduzir_erro(mensagem, probabilidade_erro=1.0):
    """
    Introduz um erro no conteúdo da mensagem, preservando o tipo e o número de sequência.
    """
    partes = mensagem.split(":")
    if len(partes) >= 3:
        # Mantém o tipo (SEND) e número de sequência
        tipo = partes[0]
        numero_sequencia = partes[1]
        conteudo = partes[2]
        
        # Introduz erro em todo o conteúdo, independente de probabilidade para pacotes específicos
        conteudo_com_erro = ''.join(random.choice('!@#$%?') if c.isalnum() else c for c in conteudo)
        partes[2] = conteudo_com_erro
        mensagem_com_erro = ":".join(partes)
    else:
        mensagem_com_erro = mensagem
    
    return mensagem_com_erro

def simular_perda():
    """
    Retorna True para simular uma perda de pacote com uma certa probabilidade.
    """
    probabilidade_perda = 0.1
    return random.random() < probabilidade_perda
