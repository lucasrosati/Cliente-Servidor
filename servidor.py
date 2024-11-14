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
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.host, self.port))
        self.socket.listen(5)
        print(f"Servidor iniciado em {self.host}:{self.port}")
        self.prob_erro_ack = 0.1
        self.tamanho_janela_recepcao = 5
        self.seq_esperado = 1
        self.mensagens_recebidas = {}
        self.pacotes_nao_confirmados = {}

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
                    if len(partes) >= 3:
                        if partes[0] in ["SEND", "ERR"]:
                            if len(partes) != 4:
                                print(f"Dados recebidos em formato incorreto: {line.strip()}")
                                continue

                            comando, seq_num_str, conteudo, checksum_recebido_str = partes
                            seq_num = int(seq_num_str)
                            checksum_recebido = int(checksum_recebido_str)
                            checksum_calculado = self.calcular_checksum(conteudo)

                            print(f"Recebido {comando}:{seq_num}:{conteudo} (Checksum recebido: {checksum_recebido}, Checksum calculado: {checksum_calculado})")

                            if checksum_recebido != checksum_calculado:
                                print(f"Erro de checksum no pacote {seq_num}")
                                self.enviar_nak(conn, seq_num)
                            elif self.protocolo == 'sr' or seq_num == self.seq_esperado:
                                self.mensagens_recebidas[seq_num] = conteudo
                                self.enviar_ack(conn, seq_num)
                                if seq_num == self.seq_esperado:
                                    self.seq_esperado += 1
                            else:
                                self.enviar_nak(conn, self.seq_esperado)
                        elif partes[0] in ["ACK_CONFIRM", "NAK_CONFIRM"]:
                            if len(partes) != 3:
                                print(f"Confirmação recebida em formato incorreto: {line.strip()}")
                                continue

                            tipo_confirmacao, seq_num_str = partes[0], partes[1]
                            checksum_recebido = int(partes[2])
                            checksum_calculado = self.calcular_checksum(f"{tipo_confirmacao}:{seq_num_str}")

                            if checksum_recebido != checksum_calculado:
                                print(f"Checksum incorreto na confirmação {tipo_confirmacao} para pacote {seq_num_str}")
                            else:
                                print(f"Recebida confirmação {tipo_confirmacao} para pacote {seq_num_str} (Checksum verificado)")
                    else:
                        print(f"Mensagem recebida em formato desconhecido: {line.strip()}")
            except Exception as e:
                print(f"Erro na comunicação: {e}")
                break
        conn.close()
        print("Conexão encerrada pelo cliente.")

    def iniciar(self):
        print("Aguardando conexões...")
        try:
            while True:
                conn, addr = self.socket.accept()
                print(f"Conexão com {addr} estabelecida.")
                client_thread = threading.Thread(target=self.receber_dados, args=(conn,))
                client_thread.daemon = True
                client_thread.start()
        except KeyboardInterrupt:
            print("\nServidor interrompido pelo usuário.")
        finally:
            self.socket.close()
            print("Socket do servidor fechado.")

def menu_servidor():
    host = "127.0.0.1"
    port = int(input("Digite a porta do servidor (12346 por padrão): ") or 12346)
    protocolo = input("Escolha o protocolo (SR para Selective Repeat, GBN para Go-Back-N): ").lower()
    cumulativo = input("Deseja confirmar pacotes cumulativamente? (S/N): ").lower() == "s"
    
    servidor = Servidor(host, port, protocolo, cumulativo)
    servidor.iniciar()

if __name__ == "__main__":
    menu_servidor()
