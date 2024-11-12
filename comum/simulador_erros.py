import random

def introduzir_erro(mensagem, probabilidade_erro):
    """
    Introduz um erro no conteúdo da mensagem com uma determinada probabilidade.
    Mantém o tipo e o número de sequência, alterando o conteúdo.
    """
    if random.random() < probabilidade_erro:
        partes = mensagem.split(":")
        if len(partes) >= 3:
            # Introduz erro no conteúdo apenas, mantendo tipo e número de sequência
            tipo, seq_num, conteudo = partes[0], partes[1], partes[2]
            conteudo_com_erro = ''.join(random.choice('!@#$%?') for _ in conteudo)  # Troca o conteúdo por caracteres de erro
            return f"{tipo}:{seq_num}:{conteudo_com_erro}"
    return mensagem

def simular_perda(probabilidade_perda):
    """
    Retorna True para simular a perda de um pacote com uma certa probabilidade.
    """
    return random.random() < probabilidade_perda

def introduzir_erro_ack(mensagem, probabilidade_erro):
    """
    Introduz um erro na mensagem de ACK/NAK com uma probabilidade.
    """
    if random.random() < probabilidade_erro:
        partes = mensagem.split(":")
        if len(partes) >= 2:
            tipo, seq_num = partes[0], partes[1]
            erro_conteudo = ''.join(random.choice('!@#$%?'))
            return f"{tipo}:{seq_num}:{erro_conteudo}"
    return mensagem

def simular_perda_ack(probabilidade_perda_ack):
    """
    Retorna True para simular a perda de um ACK com uma certa probabilidade.
    """
    return random.random() < probabilidade_perda_ack
