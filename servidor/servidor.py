# servidor/servidor.py

import socket
from protocolo_servidor import ProtocoloServidor
from simulador_erros import introduzir_erro_ack, simular_perda_ack

def iniciar_servidor():
    host = '127.0.0.1'
    porta = 12346
    modo_retransmissao = "Selective Repeat"
    confirmacao_em_grupo = True  # Ativa a confirmação em grupo

    servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        servidor_socket.bind((host, porta))
        servidor_socket.listen(5)
        print(f"Servidor iniciado em {host}:{porta} no modo {modo_retransmissao}")

        protocolo = ProtocoloServidor()
        numero_sequencia_esperado = 0
        janela_recebida = {}

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

                    if confirmacao_em_grupo:
                        if seq == numero_sequencia_esperado:
                            inicio = numero_sequencia_esperado
                            numero_sequencia_esperado += 1
                            while numero_sequencia_esperado in janela_recebida:
                                janela_recebida.pop(numero_sequencia_esperado)
                                numero_sequencia_esperado += 1
                            fim = numero_sequencia_esperado - 1
                            
                            # Envia ACK em grupo apenas se houver mais de um pacote no intervalo
                            if fim > inicio:
                                resposta = protocolo.resposta_enviar("ACK", f"{inicio}-{fim}")
                            else:
                                resposta = protocolo.resposta_enviar("ACK", f"{inicio}")
                        else:
                            resposta = protocolo.resposta_enviar("NAK", seq)
                            print("Número de sequência fora da janela, enviando NAK.")
                    else:
                        # Modo padrão de confirmação individual
                        if seq == numero_sequencia_esperado:
                            resposta = protocolo.resposta_enviar("ACK", seq)
                            numero_sequencia_esperado += 1
                        else:
                            resposta = protocolo.resposta_enviar("NAK", seq)
                            print("Número de sequência fora da janela, enviando NAK.")

                    if simular_perda_ack():
                        print("Simulando perda de ACK. Nenhuma confirmação enviada.")
                        continue

                    resposta_com_erro = introduzir_erro_ack(resposta)
                    cliente_socket.send(resposta_com_erro.encode())
                    print(f"Enviado para o cliente: {resposta_com_erro}")

            finally:
                cliente_socket.close()
                print(f"Conexão com {endereco} encerrada")

    finally:
        servidor_socket.close()
        print("Socket do servidor fechado")

if __name__ == "__main__":
    iniciar_servidor()
