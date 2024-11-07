# servidor/utils.py

import hashlib

def calcular_checksum(mensagem):
    """
    Calcula o checksum da mensagem para verificação de integridade.
    """
    return hashlib.md5(mensagem.encode()).hexdigest()

def verificar_checksum(mensagem, checksum_recebido):
    """
    Verifica se o checksum da mensagem recebida corresponde ao checksum esperado.
    """
    return calcular_checksum(mensagem) == checksum_recebido

def log_mensagem(mensagem):
    """
    Registra uma mensagem no log do servidor.
    """
    print(f"[SERVIDOR LOG] {mensagem}")
