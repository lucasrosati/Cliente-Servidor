# cliente/utils.py

import hashlib
import time

def calcular_checksum(mensagem):
    """
    Calcula o checksum da mensagem para verificação de integridade.
    """
    return hashlib.md5(mensagem.encode()).hexdigest()

def iniciar_temporizador(timeout, callback, *args):
    """
    Inicia um temporizador para retransmissão de pacotes.
    """
    time.sleep(timeout)
    callback(*args)

def log_mensagem(mensagem):
    """
    Registra uma mensagem no log do cliente.
    """
    print(f"[CLIENTE LOG] {mensagem}")
