import socket
import threading
from protocolo_servidor import ProtocoloServidor
from simulador_erros import introduzir_erro_ack, simular_perda_ack

HOST = '127.0.0.1'
PORT = 12346

protocolo = ProtocoloServidor()

def verificar_integridade(conteudo):
    caracteres_permitidos = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 "
    for caractere in conteudo:
        if caractere not in caracteres_permitidos:
            return False
    return True

def processar_pacote(mensagem, cliente_socket):
    try:
        tipo, numero_sequencia, conteudo = mensagem.split(":", 2)
        numero_sequencia = int(numero_sequencia)
        
        if not verificar_integridade(conteudo):
            print(f"Erro de integridade detectado no pacote {numero_sequencia}. Enviando NAK.")
            resposta = protocolo.mensagem_enviar("NAK", numero_sequencia)
            cliente_socket.sendall(resposta.encode())
            return

        resposta = protocolo.mensagem_enviar("ACK", numero_sequencia)
        
        if not simular_perda_ack():
            cliente_socket.sendall(resposta.encode())
            print(f"Enviado para o cliente: {resposta}")
        else:
            print(f"Simulando perda de ACK para o pacote {numero_sequencia}.")

    except ValueError:
        print(f"Erro ao processar o pacote: o conteúdo '{mensagem}' não está no formato esperado.")
        resposta = "ERRO_FORMATO"
        cliente_socket.sendall(resposta.encode())

def manipular_cliente(conexao, endereco):
    print(f"Conexão estabelecida com {endereco}")

    if conexao.recv(1024).decode() == "SYN":
        conexao.sendall("SYN-ACK".encode())
        if conexao.recv(1024).decode() == "ACK":
            print("Handshake realizado com sucesso.")
        else:
            print("Falha no handshake com o cliente.")
            conexao.close()
            return
    else:
        print("Falha no handshake com o cliente.")
        conexao.close()
        return

    try:
        while True:
            mensagem = conexao.recv(1024).decode()
            if not mensagem:
                break
            processar_pacote(mensagem, conexao)
    except Exception as e:
        print(f"Erro ao comunicar com o cliente {endereco}: {e}")
    finally:
        print(f"Conexão com {endereco} encerrada.")
        conexao.close()

def iniciar_servidor():
    servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Configuração para reutilizar a porta
    servidor_socket.bind((HOST, PORT))
    servidor_socket.listen()
    print(f"Servidor iniciado em {HOST}:{PORT} no modo Selective Repeat")

    try:
        while True:
            conexao, endereco = servidor_socket.accept()
            threading.Thread(target=manipular_cliente, args=(conexao, endereco)).start()
    except KeyboardInterrupt:
        print("Servidor encerrado.")
    finally:
        servidor_socket.close()

if __name__ == "__main__":
    iniciar_servidor()
