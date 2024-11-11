# servidor.py
import socket
import threading
from simulador_erros import introduzir_erro_ack, simular_perda_ack

HOST = '127.0.0.1'
PORT = 12346

def manipular_cliente(conexao, endereco):
    print(f"Conexão estabelecida com {endereco}")
    try:
        while True:
            # Recebe a mensagem do cliente
            mensagem = conexao.recv(1024).decode()
            if not mensagem:
                break

            print(f"Recebido do cliente {endereco}: {mensagem}")

            # Simula erro ou perda de ACK
            if simular_perda_ack():
                print("Simulando perda de ACK. Nenhuma confirmação enviada.")
                continue

            ack = f"ACK:{mensagem.split(':')[1]}"
            ack = introduzir_erro_ack(ack)  # Introduz erro no ACK se aplicável

            # Envia o ACK de volta para o cliente
            conexao.sendall(ack.encode())
            print(f"Enviado para o cliente {endereco}: {ack}")
    except Exception as e:
        print(f"Erro ao comunicar com o cliente {endereco}: {e}")
    finally:
        print(f"Conexão com {endereco} encerrada.")
        conexao.close()

def iniciar_servidor():
    servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor_socket.bind((HOST, PORT))
    servidor_socket.listen()

    print(f"Servidor iniciado em {HOST}:{PORT} no modo Selective Repeat")
    try:
        while True:
            conexao, endereco = servidor_socket.accept()
            # Cria uma nova thread para cada cliente
            thread_cliente = threading.Thread(target=manipular_cliente, args=(conexao, endereco))
            thread_cliente.start()
    except KeyboardInterrupt:
        print("Servidor encerrado.")
    finally:
        servidor_socket.close()

if __name__ == "__main__":
    iniciar_servidor()
