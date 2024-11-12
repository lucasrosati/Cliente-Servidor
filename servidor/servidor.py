import socket
import threading
import random

class Servidor:
    def __init__(self, host, port, protocolo, cumulativo):
        self.host = host
        self.port = port
        self.protocolo = protocolo
        self.cumulativo = cumulativo
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Adiciona esta linha para permitir reutilização do endereço
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        self.socket.bind((self.host, self.port))
        self.socket.listen(5)
        print(f"Servidor iniciado em {self.host}:{self.port}")
        self.prob_erro_ack = 0.1  # Probabilidade de erro nos ACKs
        self.tamanho_janela_recepcao = 5  # Tamanho inicial da janela de recepção
        self.seq_esperado = 1  # Número de sequência esperado inicia em 1
        self.mensagens_recebidas = {}  # Armazena mensagens recebidas

    def calcular_checksum(self, mensagem):
        total = 0
        for char in mensagem:
            total += ord(char)
            total = total ^ (total << 1) & 0xFFFF
        return total & 0xFFFF

    def enviar_ack(self, conn, seq_num):
        ack_data = f"ACK:{seq_num}"
        checksum = self.calcular_checksum(ack_data)
        ack = f"{ack_data}:{checksum}\n"
        if random.random() < self.prob_erro_ack:
            # Simula erro no ACK
            ack_corrompido = f"{ack_data}CORROMPIDO\n"
            conn.sendall(ack_corrompido.encode())
            print(f"Enviado ACK corrompido para pacote {seq_num}")
        else:
            conn.sendall(ack.encode())
            print(f"Enviado: {ack.strip()} (Checksum: {checksum})")

    def enviar_nak(self, conn, seq_num):
        nak_data = f"NAK:{seq_num}"
        checksum = self.calcular_checksum(nak_data)
        nak = f"{nak_data}:{checksum}\n"
        conn.sendall(nak.encode())
        print(f"Enviado: {nak.strip()} (Checksum: {checksum})")

    def receber_dados(self, conn):
        buffer = ''
        while True:
            try:
                data = conn.recv(1024).decode()
                if not data:
                    break

                buffer += data
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    partes = line.strip().split(":")
                    if len(partes) != 4:
                        print(f"Dados recebidos em formato incorreto: {line.strip()}")
                        continue

                    comando, seq_num_str, conteudo, checksum_recebido_str = partes
                    seq_num = int(seq_num_str)
                    checksum_recebido = int(checksum_recebido_str)
                    checksum_calculado = self.calcular_checksum(conteudo)

                    print(f"Recebido {comando}:{seq_num}:{conteudo} (Checksum recebido: {checksum_recebido}, Checksum calculado: {checksum_calculado})")

                    # Verifica integridade do pacote
                    if checksum_recebido != checksum_calculado:
                        print(f"Erro de checksum no pacote {seq_num}")
                        self.enviar_nak(conn, seq_num)
                    elif seq_num == self.seq_esperado:
                        # Pacote esperado, processa e envia ACK
                        self.mensagens_recebidas[seq_num] = conteudo
                        self.enviar_ack(conn, seq_num)
                        self.seq_esperado += 1
                        # Atualiza janela de recepção
                        self.tamanho_janela_recepcao += 1  # Simulação de ajuste dinâmico
                    elif seq_num > self.seq_esperado:
                        # Pacote futuro, armazena em buffer (para SR)
                        if self.protocolo == 'sr':
                            self.mensagens_recebidas[seq_num] = conteudo
                            self.enviar_ack(conn, seq_num)
                        else:
                            # No GBN, reenviar NAK para pacote esperado
                            self.enviar_nak(conn, self.seq_esperado)
                    else:
                        # Pacote duplicado ou já recebido
                        self.enviar_ack(conn, seq_num)
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

if __name__ == "__main__":
    menu_servidor()
