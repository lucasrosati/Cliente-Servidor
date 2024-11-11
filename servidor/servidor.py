import socket
import threading
from protocolo_servidor import ProtocoloServidor
from simulador_erros import simular_perda_ack, introduzir_erro_ack

# Configurações do servidor
host = "127.0.0.1"
porta = 12346
protocolo = ProtocoloServidor()

# Função para verificar a integridade do conteúdo do pacote
def verificar_integridade(conteudo):
    # Defina os caracteres permitidos ou uma condição para verificar a integridade
    caracteres_permitidos = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 "
    for caractere in conteudo:
        if caractere not in caracteres_permitidos:
            return False  # Conteúdo possui caracteres inválidos (erro de integridade)
    return True  # Conteúdo está íntegro

# Função para processar pacotes recebidos do cliente
def processar_pacote(mensagem, cliente_socket, cliente_endereco):
    tipo, numero_sequencia, conteudo = protocolo.mensagem_receber(mensagem)
    
    # Verifica a integridade do conteúdo antes de enviar ACK
    if not verificar_integridade(conteudo):
        print(f"Erro de integridade detectado no pacote {numero_sequencia}. Enviando NAK.")
        resposta = protocolo.mensagem_enviar("NAK", numero_sequencia)
    else:
        print(f"Recebido do cliente: {mensagem}")
        resposta = protocolo.mensagem_enviar("ACK", numero_sequencia)
    
    # Introduz erro no ACK, se necessário
    resposta_com_erro = introduzir_erro_ack(resposta)
    
    # Simula perda de ACK
    if not simular_perda_ack():
        print(f"Enviado para o cliente: {resposta_com_erro}")
        cliente_socket.sendall(resposta_com_erro.encode())
    else:
        print("Simulando perda de ACK. Nenhuma confirmação enviada.")

# Função principal para iniciar o servidor
def iniciar_servidor():
    servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Permite reutilizar o endereço
    servidor_socket.bind((host, porta))
    servidor_socket.listen(5)
    print(f"Servidor iniciado em {host}:{porta} no modo Selective Repeat")

    while True:
        cliente_socket, cliente_endereco = servidor_socket.accept()
        print(f"Conexão estabelecida com {cliente_endereco}")

        # Processa cada pacote recebido em uma nova thread para suportar múltiplos clientes
        threading.Thread(target=atender_cliente, args=(cliente_socket, cliente_endereco)).start()

def atender_cliente(cliente_socket, cliente_endereco):
    try:
        while True:
            mensagem = cliente_socket.recv(1024).decode()
            if not mensagem:
                break
            processar_pacote(mensagem, cliente_socket, cliente_endereco)
    except Exception as e:
        print(f"Erro ao processar pacote: {e}")
    finally:
        print(f"Conexão com o cliente {cliente_endereco} encerrada.")
        cliente_socket.close()

# Tratamento para garantir que o socket será fechado
if __name__ == "__main__":
    try:
        iniciar_servidor()
    finally:
        print("Servidor encerrado.")
