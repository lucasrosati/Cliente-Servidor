import socket
import threading
import random
import time
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
        self.naks_recebidos = set()
        self.dados_enviados = {}
        self.timeout = 2
        self.carros = self.carregar_carros()

    def carregar_carros(self):
        path = os.path.join(os.getcwd(), "carros.txt")
        try:
            with open(path, "r") as file:
                carros = [linha.strip() for linha in file.read().split(",")]
                return carros[:self.num_mensagens]
        except FileNotFoundError:
            print("Arquivo carros.txt não encontrado. Usando mensagens genéricas.")
            return [f"Mensagem {i}" for i in range(1, self.num_mensagens + 1)]

    def calcular_checksum(self, mensagem):
        return sum(ord(c) for c in mensagem) % 65536

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

    def receber_respostas(self):
        buffer = ""
        while len(self.acks_recebidos) < self.num_mensagens:
            try:
                data = self.socket.recv(1024).decode()
                if not data:
                    break
                buffer += data
                while '\n' in buffer:
                    linha, buffer = buffer.split('\n', 1)
                    tipo, seq_num, checksum = linha.split(":")
                    seq_num = int(seq_num)
                    checksum = int(checksum)
                    esperado = f"{tipo}:{seq_num}"
                    if self.calcular_checksum(esperado) == checksum:
                        if tipo == "ACK":
                            self.acks_recebidos.add(seq_num)
                            print(f"Recebido ACK para pacote {seq_num}")
                        elif tipo == "NAK":
                            self.naks_recebidos.add(seq_num)
                            print(f"Recebido NAK para pacote {seq_num}, retransmitindo...")
                            self.enviar_pacote(seq_num, self.carros[seq_num - 1])
                    else:
                        print(f"Resposta corrompida: {linha}")
            except Exception as e:
                print(f"Erro ao receber resposta: {e}")

    def iniciar_envio(self):
        threading.Thread(target=self.receber_respostas, daemon=True).start()
        for seq_num in range(1, self.num_mensagens + 1):
            if seq_num not in self.acks_recebidos:
                self.enviar_pacote(seq_num, self.carros[seq_num - 1])
            time.sleep(0.1)
        while len(self.acks_recebidos) < self.num_mensagens:
            time.sleep(0.1)

    def fechar_conexao(self):
        self.socket.close()
        print("Conexão encerrada.")

def menu_cliente():
    host = input("Digite o endereço do servidor (127.0.0.1 por padrão): ") or "127.0.0.1"
    port = int(input("Digite a porta do servidor (12346 por padrão): ") or 12346)
    prob_erro = float(input("Digite a probabilidade de erro (ex: 0.1): "))
    janela = int(input("Digite o tamanho inicial da janela: "))
    num_mensagens = int(input("Digite o número de mensagens a enviar: "))

    cliente = Cliente(host, port, prob_erro, janela, num_mensagens)
    cliente.iniciar_envio()
    cliente.fechar_conexao()

if __name__ == "__main__":
    menu_cliente()
