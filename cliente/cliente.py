import socket
import threading
import time
from protocolo_cliente import ProtocoloCliente
from simulador_erros import introduzir_erro, simular_perda

HOST = '127.0.0.1'
PORT = 12346
TEMPO_TIMEOUT = 2  # Timeout para retransmissão de pacotes

# Lista de pacotes específicos para introduzir erros
pacotes_com_erro = [10, 15, 20]  # Defina aqui os números de sequência dos pacotes que terão erro

# Classe de cliente
class Cliente:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((HOST, PORT))
        self.protocolo = ProtocoloCliente()
        self.ack_recebido = {}  # Dicionário para armazenar a confirmação de pacotes
        print(f"Conectado ao servidor em {HOST}:{PORT}")
        
        if self.realizar_handshake():
            print("Handshake realizado com sucesso.")
        else:
            print("Handshake falhou.")
            self.socket.close()

    def realizar_handshake(self):
        try:
            # Envia o pedido de conexão "SYN"
            self.socket.sendall("SYN".encode())
            resposta = self.socket.recv(1024).decode()
            
            # Espera "SYN-ACK" do servidor
            if resposta == "SYN-ACK":
                # Envia confirmação "ACK"
                self.socket.sendall("ACK".encode())
                return True
            else:
                print("Falha no handshake: resposta inesperada")
                return False
        except Exception as e:
            print(f"Erro durante o handshake: {e}")
            return False

    def enviar_pacote(self, numero_sequencia, conteudo):
        mensagem = self.protocolo.mensagem_enviar("SEND", conteudo, numero_sequencia)

        # Verifica se o pacote está na lista de pacotes com erro
        if numero_sequencia in pacotes_com_erro:
            mensagem = introduzir_erro(mensagem)  # Introduz erro específico no pacote

        # Simula perda de pacote
        if not simular_perda():
            self.socket.sendall(mensagem.encode())
            print(f"Enviado para o servidor: {mensagem}")
        else:
            print(f"Pacote {numero_sequencia} simulado como perdido.")

    def receber_ack(self):
        while True:
            try:
                resposta = self.socket.recv(1024).decode()
                if resposta:
                    tipo, seq, conteudo = self.protocolo.mensagem_receber(resposta)
                    print(f"Resposta do servidor: Tipo={tipo}, Número de Sequência={seq}, Conteúdo={conteudo}")
                    if tipo == "ACK":
                        self.ack_recebido[int(seq)] = True
                    elif tipo == "NAK":
                        print(f"Recebido NAK para o pacote {seq}. Retransmitindo...")
                        self.enviar_pacote(int(seq), f"Pacote {seq}")
            except Exception as e:
                print(f"Erro ao receber ACK: {e}")
                break

    def iniciar(self):
        # Inicia a thread para receber ACKs
        thread_receber_ack = threading.Thread(target=self.receber_ack)
        thread_receber_ack.start()

        # Envia pacotes de dados sequencialmente
        for i in range(50): # Envio de pacotes de forma sequencial (unitária ou em rajada)
            if i not in self.ack_recebido:
                self.enviar_pacote(i, f"Pacote {i}")
                time.sleep(0.5)  # Intervalo entre envios para facilitar visualização

        # Aguarda a finalização da thread de recepção de ACKs
        thread_receber_ack.join()
        self.socket.close()

if __name__ == "__main__":
    cliente = Cliente()
    cliente.iniciar()
