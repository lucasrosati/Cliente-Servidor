import socket
import threading
import random
import sys
import os
import time

class Cliente:
    def __init__(self, host, port, protocolo, modo_envio, probabilidade_erro, tamanho_janela, num_mensagens):
        self.host = host
        self.port = port
        self.protocolo = protocolo
        self.modo_envio = modo_envio
        self.prob_erro = probabilidade_erro
        self.tamanho_janela_inicial = tamanho_janela
        self.tamanho_janela = tamanho_janela
        self.num_mensagens = num_mensagens
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        self.timeout = 2
        self.lock = threading.Lock()
        self.dados = []
        self.acks = set()
        self.seq_enviados = set()
        self.inicio_janela = 1  # Inicia em 1
        self.fim_janela = self.inicio_janela + self.tamanho_janela - 1
        self.carregar_dados()
        self.cwnd = 1  # Janela de congestionamento
        self.ssthresh = 8  # Limite de slow start
        self.duplicated_acks = 0  # Contador de ACKs duplicados

    def carregar_dados(self):
        try:
            path = os.path.join(sys.path[0], "carros.txt")
            with open(path, "r") as file:
                self.dados = [carro.strip() for carro in file.read().split(",")]
        except FileNotFoundError:
            print("Arquivo carros.txt não encontrado. Usando dados de exemplo.")
            self.dados = [f"Carro{i+1}" for i in range(self.num_mensagens)]
        self.dados = self.dados[:self.num_mensagens]

    def calcular_checksum(self, mensagem):
        total = 0
        for char in mensagem:
            total += ord(char)
            total = total ^ (total << 1) & 0xFFFF
        return total & 0xFFFF

    def enviar_pacote(self, pacote, seq_num):
        checksum = self.calcular_checksum(pacote)
        if random.random() < self.prob_erro:
            pacote = f"ERR:{seq_num}:{pacote[::-1]}:{checksum}\n"
            print(f"Simulando falha no pacote {seq_num}")
        else:
            pacote = f"SEND:{seq_num}:{pacote}:{checksum}\n"
        # Simulação de perda de pacote
        if random.random() < self.prob_erro:
            print(f"Simulando perda do pacote {seq_num}")
            return  # Não envia o pacote
        try:
            self.socket.sendall(pacote.encode())
            print(f"Enviado: {pacote.strip()} (Checksum: {checksum})")
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
                # Ajuste da janela de congestionamento
                self.ssthresh = max(self.cwnd // 2, 1)
                self.cwnd = 1
                self.duplicated_acks = 0

    def receber_acks(self):
        buffer = ''
        total_mensagens = len(self.dados)
        while len(self.acks) < total_mensagens:
            try:
                data = self.socket.recv(1024).decode()
                if not data:
                    break
                buffer += data
                while '\n' in buffer:
                    resposta, buffer = buffer.split('\n', 1)
                    resposta = resposta.strip()
                    partes = resposta.split(":")
                    if len(partes) != 3:
                        print(f"Resposta inválida: {resposta}")
                        continue
                    tipo, seq_num_str, checksum_str = partes
                    try:
                        seq_num = int(seq_num_str)
                        checksum_recebido = int(checksum_str)
                        checksum_calculado = self.calcular_checksum(f"{tipo}:{seq_num}")
                    except ValueError:
                        print(f"ACK/NAK corrompido recebido: {resposta}")
                        continue  # Ignora ACK/NAK corrompido
                    if checksum_recebido != checksum_calculado:
                        print(f"Checksum incorreto para {tipo}:{seq_num}")
                        continue  # Ignora ACK/NAK com checksum incorreto
                    with self.lock:
                        if tipo == "ACK":
                            if seq_num in self.acks:
                                self.duplicated_acks += 1
                                print(f"ACK duplicado recebido para pacote {seq_num}")
                                if self.duplicated_acks == 3:
                                    print("Recebidos 3 ACKs duplicados, iniciando Fast Retransmit")
                                    self.ssthresh = max(self.cwnd // 2, 1)
                                    self.cwnd = self.ssthresh + 3
                            else:
                                self.acks.add(seq_num)
                                print(f"Recebido ACK para pacote {seq_num}")
                                self.duplicated_acks = 0
                                # Ajuste da janela de congestionamento
                                if self.cwnd < self.ssthresh:
                                    self.cwnd += 1  # Slow Start
                                else:
                                    self.cwnd += 1 / self.cwnd  # Congestion Avoidance
                                # Atualiza janela de envio
                                self.inicio_janela = max(self.acks) + 1 if self.acks else 1
                                self.fim_janela = self.inicio_janela + int(self.cwnd) - 1
                        elif tipo == "NAK":
                            print(f"Recebido NAK para pacote {seq_num}, retransmitindo...")
                            self.enviar_pacote(self.dados[seq_num - 1], seq_num)
                            self.iniciar_temporizador(seq_num, self.dados[seq_num - 1])
            except Exception as e:
                print(f"Erro ao receber ACK/NAK: {e}")
                break
        print("Recebimento de ACKs finalizado.")

    def enviar_dados(self):
        threading.Thread(target=self.receber_acks, daemon=True).start()
        total_mensagens = len(self.dados)
        while self.inicio_janela <= total_mensagens:
            with self.lock:
                for seq_num in range(self.inicio_janela, min(self.fim_janela + 1, total_mensagens + 1)):
                    if seq_num not in self.seq_enviados:
                        pacote = self.dados[seq_num - 1]  # Ajuste no índice
                        self.enviar_pacote(pacote, seq_num)
                        self.seq_enviados.add(seq_num)
                        self.iniciar_temporizador(seq_num, pacote)
            time.sleep(0.1)
        print("Envio de dados finalizado.")

    def iniciar(self):
        self.enviar_dados()
        while threading.active_count() > 1:
            time.sleep(0.1)
        self.fechar_conexao()

    def fechar_conexao(self):
        self.socket.close()
        print("Conexão encerrada com o servidor.")

def menu_cliente():
    host = input("Digite o endereço do servidor (127.0.0.1 por padrão): ") or "127.0.0.1"
    port = int(input("Digite a porta do servidor (12346 por padrão): ") or 12346)
    protocolo = input("Escolha o protocolo (SR para Selective Repeat, GBN para Go-Back-N): ").lower()
    modo_envio = input("Escolha o modo de envio (unico ou rajada): ").lower()
    probabilidade_erro = float(input("Digite a probabilidade de erro para gerar NAKs (ex: 0.1): "))
    tamanho_janela = int(input("Digite o tamanho inicial da janela de envio: "))
    num_mensagens = int(input("Digite o número total de mensagens a serem enviadas: "))
    
    cliente = Cliente(host, port, protocolo, modo_envio, probabilidade_erro, tamanho_janela, num_mensagens)
    cliente.iniciar()

if __name__ == "__main__":
    menu_cliente()
