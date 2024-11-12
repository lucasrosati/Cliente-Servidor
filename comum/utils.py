import time

def calcular_checksum(mensagem):
    """
    Calcula um checksum simples somando os valores ASCII dos caracteres.
    """
    checksum = sum(ord(char) for char in mensagem) % 256  # Mantém o valor no intervalo de um byte (0-255)
    return checksum

def verificar_checksum(mensagem, checksum_recebido):
    """
    Verifica se o checksum calculado da mensagem corresponde ao checksum recebido.
    """
    return calcular_checksum(mensagem) == checksum_recebido

def iniciar_temporizador(timeout, callback, *args):
    """
    Inicia um temporizador para acionar uma função de retransmissão de pacotes.
    """
    time.sleep(timeout)
    callback(*args)

def log_mensagem(mensagem):
    """
    Registra uma mensagem de log.
    """
    print(f"[LOG] {mensagem}")
