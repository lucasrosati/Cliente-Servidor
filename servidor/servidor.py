import socket
import threading

class Servidor:
    def __init__(self, host, port, protocolo, cumulativo):
        self.host = host
        self.port = port
        self.protocolo = protocolo
        self.cumulativo = cumulativo
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.socket.listen(5)
        print(f"Servidor iniciado em {self.host}:{self.port}")

    def calcular_checksum(self, mensagem):
        total = 0
        for char in mensagem:
            total += ord(char)
            total = total ^ (total << 1) & 0xFFFF  # XOR para evitar inversão simples
        return total & 0xFFFF  # Limita ao intervalo de 16 bits

    def receber_dados(self, conn):
        while True:
            try:
                data = conn.recv(1024).decode()
                if not data:
                    break

                partes = data.strip().split(":")
                if len(partes) != 4:
                    print(f"Dados recebidos em formato incorreto: {data.strip()}")
                    continue

                comando, seq_num, conteudo, checksum_recebido = partes
                checksum_calculado = self.calcular_checksum(conteudo)

                if int(checksum_recebido) == checksum_calculado:
                    print(f"Recebido {comando}:{seq_num}:{conteudo} - Checksum Calculado: {checksum_calculado} - Válido")
                    resposta = f"ACK:{seq_num}\n"
                else:
                    print(f"Recebido {comando}:{seq_num}:{conteudo} - Checksum Calculado: {checksum_calculado} - Inválido")
                    resposta = f"NAK:{seq_num}\n"
                
                conn.sendall(resposta.encode())
                print(f"Enviado: {resposta.strip()}")
            except Exception as e:
                print(f"Erro na comunicação: {e}")
                break
        conn.close()
        print("Conexão encerrada pelo cliente.")

    def iniciar(self):
        print("Aguardando conexões...")
        while True:
            conn, addr = self.socket.accept()
            print(f"Conexão com {addr} estabelecida.")
            client_thread = threading.Thread(target=self.receber_dados, args=(conn,))
            client_thread.daemon = True
            client_thread.start()

def menu_servidor():
    host = "127.0.0.1"
    port = int(input("Digite a porta do servidor (12346 por padrão): ") or 12346)
    protocolo = input("Escolha o protocolo (SR para Selective Repeat, GBN para Go-Back-N): ").lower()
    cumulativo = input("Deseja confirmar pacotes cumulativamente? (S/N): ").lower() == "s"
    
    servidor = Servidor(host, port, protocolo, cumulativo)
    servidor.iniciar()

menu_servidor()
