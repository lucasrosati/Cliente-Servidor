# servidor/servidor.py

import socket
from protocolo_servidor import ProtocoloServidor
from simulador_erros import introduzir_erro_ack, simular_perda_ack

def iniciar_servidor():
    host = '127.0.0.1'  # localhost
    porta = 12346
    modo_retransmissao = "Selective Repeat"  # Pode ser "Go-Back-N" ou "Selective Repeat"

    # Criação do socket do servidor com a opção SO_REUSEADDR
    servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Permite reutilizar a porta imediatamente

    try:
        servidor_socket.bind((host, porta))
        servidor_socket.listen(5)
        print(f"Servidor iniciado em {host}:{porta} no modo {modo_retransmissao}")

        protocolo = ProtocoloServidor()
        numero_sequencia_esperado = 0
        janela_recebida = {}  # Armazena pacotes fora de ordem para o modo Selective Repeat

        while True:
            cliente_socket, endereco = servidor_socket.accept()
            print(f"Conexão estabelecida com {endereco}")

            try:
                while True:
                    dados = cliente_socket.recv(1024).decode()
                    if not dados:
                        break
                    print(f"Recebido do cliente: {dados}")

                    tipo, seq, conteudo = protocolo.resposta_receber(dados)

                    if modo_retransmissao == "Go-Back-N":
                        # No modo Go-Back-N, só aceita o pacote se estiver na sequência exata
                        if seq == numero_sequencia_esperado:
                            resposta = protocolo.resposta_enviar("ACK", seq)
                            numero_sequencia_esperado += 1
                        else:
                            resposta = protocolo.resposta_enviar("NAK", seq)
                            print("Número de sequência fora da janela, enviando NAK.")

                    elif modo_retransmissao == "Selective Repeat":
                        # No modo Selective Repeat, aceita pacotes fora de ordem e armazena até o número esperado
                        if seq == numero_sequencia_esperado:
                            resposta = protocolo.resposta_enviar("ACK", seq)
                            numero_sequencia_esperado += 1
                            # Envia ACKs para qualquer pacote armazenado em ordem
                            while numero_sequencia_esperado in janela_recebida:
                                janela_recebida.pop(numero_sequencia_esperado)
                                numero_sequencia_esperado += 1
                        elif seq > numero_sequencia_esperado:
                            resposta = protocolo.resposta_enviar("ACK", seq)
                            janela_recebida[seq] = conteudo  # Armazena pacotes fora de ordem
                        else:
                            # Se o pacote estiver fora da janela de repetição, envia NAK
                            resposta = protocolo.resposta_enviar("NAK", seq)
                            print("Número de sequência fora da janela, enviando NAK.")

                    # Simula perda de ACK
                    if simular_perda_ack():
                        print("Simulando perda de ACK. Nenhuma confirmação enviada.")
                        continue

                    # Introduz erro na resposta ACK/NAK
                    resposta_com_erro = introduzir_erro_ack(resposta)
                    cliente_socket.send(resposta_com_erro.encode())
                    print(f"Enviado para o cliente: {resposta_com_erro}")

            finally:
                cliente_socket.close()
                print(f"Conexão com {endereco} encerrada")

    finally:
        servidor_socket.close()  # Garante que o socket do servidor é fechado ao encerrar
        print("Socket do servidor fechado")

if __name__ == "__main__":
    iniciar_servidor()
