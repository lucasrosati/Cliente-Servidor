import socket
import threading
import time
import random
import os

class Cliente:
    def __init__(self, host, port, prob_erro, janela, num_mensagens):
        self.host = host
        self.port = port
        self.prob_erro = prob_erro
        self.janela = janela
        self.num_mensagens = num_mensagens
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        self.acks_recebidos = set()
        self.dados_enviados = {}
        self.timeout = 2  # Timeout em segundos
        self.timer_threads = {}
        self.buffer_dados = []

    def enviar_handshake(self):
        handshake_msg = f"HANDSHAKE:PROTOCOL:SR:WINDOW:{self.janela}"
        self.socket.sendall(f"{handshake_msg}\n".encode())
        print(f"Handshake enviado: {handshake_msg}")
        ack_handshake = self.socket.recv(1024).decode().strip()
        
        if ack_handshake.startswith("ACK_HANDSHAKE"):
            print(f"Handshake confirmado pelo servidor: {ack_handshake}")
        else:
            print("Falha no handshake. Encerrando conexão.")
            self.socket.close()
            exit()



    def carregar_dados(self):
        path = os.path.join(os.getcwd(), "carros.txt")
        try:
            with open(path, "r") as arquivo:
                self.buffer_dados = [linha.strip() for linha in arquivo.read().split(",")]
        except FileNotFoundError:
            print("Arquivo carros.txt não encontrado. Usando mensagens genéricas.")
            self.buffer_dados = [f"Mensagem {i + 1}" for i in range(self.num_mensagens)]

    def calcular_checksum(self, mensagem):
        return sum(ord(c) for c in mensagem) & 0xFFFF

    def enviar_pacote(self, seq_num, mensagem):
        checksum = self.calcular_checksum(mensagem)
        if random.random() < self.prob_erro:
            mensagem = f"ERR:{seq_num}:{mensagem[::-1]}:{checksum}"
            print(f"Simulando falha no pacote {seq_num}")
        else:
            mensagem = f"SEND:{seq_num}:{mensagem}:{checksum}"
        try:
            self.socket.sendall(f"{mensagem}\n".encode())
            self.dados_enviados[seq_num] = mensagem
            print(f"Enviado: {mensagem}")
        except Exception as e:
            print(f"Erro ao enviar pacote {seq_num}: {e}")

    def iniciar_timer(self, seq_num):
        def timer_expirado():
            if seq_num not in self.acks_recebidos:
                print(f"Timeout para pacote {seq_num}, retransmitindo...")
                self.enviar_pacote(seq_num, self.buffer_dados[seq_num - 1])
                self.iniciar_timer(seq_num)

        if seq_num in self.timer_threads:
            self.timer_threads[seq_num].cancel()

        timer = threading.Timer(self.timeout, timer_expirado)
        timer.start()
        self.timer_threads[seq_num] = timer

    def cancelar_timer(self, seq_num):
        if seq_num in self.timer_threads:
            self.timer_threads[seq_num].cancel()
            del self.timer_threads[seq_num]

    def receber_respostas(self):
        buffer = ""
        while len(self.acks_recebidos) < self.num_mensagens:
            try:
                data = self.socket.recv(1024).decode()
                if not data:
                    break
                buffer += data
                while "\n" in buffer:
                    linha, buffer = buffer.split("\n", 1)
                    partes = linha.split(":")
                    if len(partes) < 3:
                        continue
                    tipo, seq_num_str, checksum_str = partes
                    seq_num = int(seq_num_str)
                    checksum = int(checksum_str)

                    esperado = f"{tipo}:{seq_num}"
                    if self.calcular_checksum(esperado) == checksum:
                        if tipo == "ACK":
                            print(f"Recebido ACK para pacote {seq_num}")
                            self.acks_recebidos.add(seq_num)
                            self.cancelar_timer(seq_num)
                        elif tipo == "NAK":
                            print(f"Recebido NAK para pacote {seq_num}, retransmitindo...")
                            if seq_num not in self.acks_recebidos:
                                self.enviar_pacote(seq_num, self.buffer_dados[seq_num - 1])
                                self.iniciar_timer(seq_num)
                    else:
                        print(f"Resposta corrompida: {linha}")
            except Exception as e:
                print(f"Erro ao receber resposta: {e}")

    def iniciar_envio(self):
        self.carregar_dados()
        threading.Thread(target=self.receber_respostas, daemon=True).start()

        for seq_num in range(1, self.num_mensagens + 1):
            if seq_num not in self.acks_recebidos:
                self.enviar_pacote(seq_num, self.buffer_dados[seq_num - 1])
                self.iniciar_timer(seq_num)

        while len(self.acks_recebidos) < self.num_mensagens:
            time.sleep(1)

        print("Todos os pacotes foram confirmados. Encerrando...")

    def fechar_conexao(self):
        print("Aguardando confirmação final dos ACKs...")
        time.sleep(1)
        self.socket.close()
        print("Conexão encerrada.")

def menu_cliente():
    host = input("Digite o endereço do servidor (127.0.0.1 por padrão): ") or "127.0.0.1"
    port = int(input("Digite a porta do servidor (12346 por padrão): ") or 12346)
    prob_erro = float(input("Digite a probabilidade de erro (ex: 0.1): "))
    janela = int(input("Digite o tamanho inicial da janela: "))
    num_mensagens = int(input("Digite o número de mensagens a enviar: "))
    modo_envio = input("Escolha o modo de envio (unico ou rajada): ").lower()

    cliente = Cliente(host, port, prob_erro, janela, num_mensagens)
    cliente.enviar_handshake()
    if modo_envio == "unico":
        cliente.iniciar_envio()
    elif modo_envio == "rajada":
        cliente.iniciar_envio()  # Reutiliza a lógica de envio padrão para rajada
    cliente.fechar_conexao()

if __name__ == "__main__":
    menu_cliente()
