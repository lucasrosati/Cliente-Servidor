# cliente/cliente.py
import socket
import time
import threading
from protocolo_cliente import ProtocoloCliente
from simulador_erros import introduzir_erro, simular_perda

# Variável global para armazenar ACKs recebidos
ack_received = [False] * 100  # Controle de ACKs recebidos para até 100 pacotes (exemplo)

# Variáveis para o relatório de status
pacotes_enviados = 0
pacotes_retransmitidos = 0

def iniciar_cliente():
    global cliente_socket, pacotes_enviados, pacotes_retransmitidos

    host = '127.0.0.1'
    porta = 12346  # Porta atualizada para evitar conflitos

    cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    protocolo = ProtocoloCliente()

    # Configurações da janela deslizante e temporizador
    window_size = 3  # Quantidade de pacotes que podem ser enviados sem confirmação
    timeout = 2  # Tempo limite para retransmissão em segundos
    base = 0  # Primeiro número de sequência da janela
    next_seq_num = 0  # Próximo número de sequência a ser enviado

    # Função para lidar com a recepção de ACKs
    def receber_ack():
        nonlocal base  # Permite modificar a variável base dentro da função
        while True:
            try:
                resposta = cliente_socket.recv(1024).decode()
                tipo, seq, conteudo = protocolo.mensagem_receber(resposta)

                # Ignora mensagens com número de sequência inválido
                if seq is None:
                    print("Mensagem inválida recebida e ignorada.")
                    continue

                print(f"Resposta do servidor: Tipo={tipo}, Número de Sequência={seq}, Conteúdo={conteudo}")

                if tipo == "ACK" and seq >= base:
                    # Marca o ACK como recebido e desliza a janela
                    ack_received[seq] = True
                    while ack_received[base]:  # Desliza a janela até o próximo pacote não confirmado
                        base += 1

            except OSError:
                break  # Sai do loop se o socket for fechado

    try:
        cliente_socket.connect((host, porta))
        print(f"Conectado ao servidor em {host}:{porta}")

        # Inicia a thread para receber ACKs após a conexão estar estabelecida
        threading.Thread(target=receber_ack, daemon=True).start()

        while True:
            # Envia pacotes enquanto houver espaço na janela
            while next_seq_num < base + window_size:
                mensagem = protocolo.mensagem_enviar("SEND", f"Pacote {next_seq_num}", next_seq_num)
                mensagem_com_erro = introduzir_erro(mensagem)

                if not simular_perda():
                    cliente_socket.send(mensagem_com_erro.encode())
                    pacotes_enviados += 1
                    print(f"Enviado para o servidor: {mensagem_com_erro}")
                else:
                    print(f"Pacote {next_seq_num} simulado como perdido.")

                # Inicia o temporizador para o pacote
                threading.Timer(timeout, lambda seq=next_seq_num: retransmitir_pacote(seq)).start()

                next_seq_num += 1
                time.sleep(0.5)  # Delay para simular intervalo entre envios

    finally:
        cliente_socket.close()
        print("Conexão encerrada")
        print(f"Relatório de Status:")
        print(f"Pacotes enviados: {pacotes_enviados}")
        print(f"Pacotes retransmitidos: {pacotes_retransmitidos}")

def retransmitir_pacote(seq):
    """
    Retransmite o pacote caso o ACK não tenha sido recebido.
    """
    global cliente_socket, pacotes_retransmitidos
    protocolo = ProtocoloCliente()
    if not ack_received[seq]:  # Verifica se o ACK foi recebido
        mensagem = protocolo.mensagem_enviar("SEND", f"Pacote {seq}", seq)
        cliente_socket.send(mensagem.encode())
        pacotes_retransmitidos += 1
        print(f"Retransmitindo pacote {seq} devido ao timeout.")

if __name__ == "__main__":
    iniciar_cliente()
