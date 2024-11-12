import socket
import threading
import random
import sys
import os
import time

class Cliente:
    def __init__(self, host, port, protocolo, modo_envio, probabilidade_erro, tamanho_janela):
        self.host = host
        self.port = port
        self.protocolo = protocolo
        self.modo_envio = modo_envio
        self.prob_erro = probabilidade_erro
        self.tamanho_janela = tamanho_janela
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        self.timeout = 2
        self.lock = threading.Lock()
        self.dados = []
        self.acks = set()
        self.carregar_dados()

    def carregar_dados(self):
        try:
            path = os.path.join(sys.path[0], "carros.txt")
            with open(path, "r") as file:
                self.dados = [carro.strip() for carro in file.read().split(",")]
        except FileNotFoundError:
            print("Arquivo carros.txt não encontrado.")

    def calcular_checksum(self, mensagem):
        total = 0
        for char in mensagem:
            total += ord(char)
            total = total ^ (total << 1) & 0xFFFF  # XOR para evitar inversão simples
        return total & 0xFFFF  # Limita ao intervalo de 16 bits

    def enviar_pacote(self, pacote, seq_num):
        checksum = self.calcular_checksum(pacote)
        if random.random() < self.prob_erro:
            pacote = f"ERR:{seq_num}:{pacote[::-1]}:{checksum}\n"
            print(f"Simulando falha no pacote {seq_num}")
        else:
            pacote = f"SEND:{seq_num}:{pacote}:{checksum}\n"
        try:
            self.socket.sendall(pacote.encode())
            print(f"Enviado: {pacote.strip()}")
        except Exception as e:
            print(f"Erro ao enviar pacote {seq_num}: {e}")

    def iniciar_temporizador(self, seq_num, pacote):
        timer_thread = threading.Thread(target=self.temporizador, args=(seq_num, pacote))
        timer_thread.daemon = True
        timer_thread.start()

    def temporizador(self, seq_num, pacote):
        time.sleep(self.timeout)
        with self.lock:
            if seq_num not in self.acks:
                print(f"Timeout para pacote {seq_num}, retransmitindo...")
                self.enviar_pacote(pacote, seq_num)
                self.iniciar_temporizador(seq_num, pacote)

    def receber_acks(self):
        while len(self.acks) < self.tamanho_janela:
            try:
                resposta = self.socket.recv(1024).decode().strip()
                if resposta.startswith("ACK:"):
                    ack_num = int(resposta.split(":")[1])
                    with self.lock:
                        if ack_num not in self.acks:
                            self.acks.add(ack_num)
                            print(f"Recebido ACK para pacote {ack_num}")
                elif resposta.startswith("NAK:"):
                    nak_num = int(resposta.split(":")[1])
                    print(f"Recebido NAK para pacote {nak_num}, retransmitindo...")
                    self.enviar_pacote(self.dados[nak_num], nak_num)
            except Exception as e:
                print(f"Erro ao receber ACK/NAK: {e}")
                break

    def enviar_dados(self):
        threading.Thread(target=self.receber_acks, daemon=True).start()
        for seq_num in range(min(self.tamanho_janela, len(self.dados))):
            pacote = self.dados[seq_num]
            self.enviar_pacote(pacote, seq_num)
            time.sleep(0.1)  # Pausa para desacelerar a rajada

    def iniciar(self):
        self.enviar_dados()

    def fechar_conexao(self):
        self.socket.close()
        print("Conexão encerrada com o servidor.")

def menu_cliente():
    host = input("Digite o endereço do servidor (127.0.0.1 por padrão): ") or "127.0.0.1"
    port = int(input("Digite a porta do servidor (12346 por padrão): ") or 12346)
    protocolo = input("Escolha o protocolo (SR para Selective Repeat, GBN para Go-Back-N): ").lower()
    modo_envio = input("Escolha o modo de envio (unico ou rajada): ").lower()
    probabilidade_erro = float(input("Digite a probabilidade de erro para gerar NAKs (ex: 0.1): "))
    tamanho_janela = int(input("Digite o número total de mensagens a serem enviadas: "))
    
    cliente = Cliente(host, port, protocolo, modo_envio, probabilidade_erro, tamanho_janela)
    cliente.iniciar()

menu_cliente()
