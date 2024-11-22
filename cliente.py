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

    def carregar_dados(self):
        """
        Carrega os dados do arquivo carros.txt ou gera mensagens genéricas caso o arquivo não exista.
        """
        path = os.path.join(os.getcwd(), "carros.txt")
        try:
            with open(path, "r") as arquivo:
                self.buffer_dados = [linha.strip() for linha in arquivo.read().split(",")]
        except FileNotFoundError:
            print("Arquivo carros.txt não encontrado. Usando mensagens genéricas.")
            self.buffer_dados = [f"Mensagem {i + 1}" for i in range(self.num_mensagens)]

    def calcular_checksum(self, mensagem):
        """
        Calcula o checksum da mensagem.
        """
        return sum(ord(c) for c in mensagem) & 0xFFFF

    def enviar_pacote(self, seq_num, mensagem):
        """
        Envia um pacote com possível introdução de erro para simular falhas na transmissão.
        """
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
        """
        Inicia um timer para retransmissão caso não receba um ACK no tempo esperado.
        """
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
        """
        Cancela o timer de retransmissão para pacotes confirmados.
        """
        if seq_num in self.timer_threads:
            self.timer_threads[seq_num].cancel()
            del self.timer_threads[seq_num]

    def receber_respostas(self):
        """
        Recebe respostas do servidor (ACKs ou NAKs) e processa-as.
        """
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
                            self.enviar_pacote(seq_num, self.buffer_dados[seq_num - 1])
                            self.iniciar_timer(seq_num)
                    else:
                        print(f"Resposta corrompida: {linha}")
            except Exception as e:
                print(f"Erro ao receber resposta: {e}")

    def iniciar_envio(self):
        """
        Inicia o envio de pacotes e gerencia retransmissões e timeouts.
        """
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
        time.sleep(1)  # Aguarda para garantir o envio de ACKs finais
        self.socket.close()
        print("Conexão encerrada.")



def menu_cliente():
    """
    Menu de configuração do cliente.
    """
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
