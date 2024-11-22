import socket
import threading

class Servidor:
    def __init__(self, host, port, protocolo, cumulativo):
        self.host = host
        self.port = port
        self.protocolo = protocolo  # 'SR' para Selective Repeat, 'GBN' para Go-Back-N
        self.cumulativo = cumulativo  # Confirmação cumulativa (True/False)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.host, self.port))
        self.socket.listen(5)
        self.seq_esperado = 1
        self.mensagens_recebidas = {}
        self.pacotes_fora_de_ordem = {}  # Armazena pacotes fora de ordem

    def calcular_checksum(self, mensagem):
        return sum(ord(c) for c in mensagem) & 0xFFFF

    def enviar_ack(self, conn, seq_num):
        ack_data = f"ACK:{seq_num}"
        checksum = self.calcular_checksum(ack_data)
        ack = f"{ack_data}:{checksum}\n"
        conn.sendall(ack.encode())
        print(f"Enviado: {ack.strip()} (Checksum: {checksum})")

    def enviar_nak(self, conn, seq_num):
        nak_data = f"NAK:{seq_num}"
        checksum = self.calcular_checksum(nak_data)
        nak = f"{nak_data}:{checksum}\n"
        conn.sendall(nak.encode())
        print(f"Enviado: {nak.strip()} (Checksum: {checksum})")

    def processar_pacote(self, conn, seq_num, conteudo, checksum_recebido):
        checksum_calculado = self.calcular_checksum(conteudo)

        if checksum_recebido != checksum_calculado:
            print(f"Erro de checksum no pacote {seq_num}: {conteudo}")
            self.enviar_nak(conn, seq_num)
        elif seq_num == self.seq_esperado:
            # Pacote na ordem esperada
            print(f"Pacote {seq_num} confirmado: {conteudo}")
            self.mensagens_recebidas[seq_num] = conteudo
            self.enviar_ack(conn, seq_num)
            self.seq_esperado += 1

            # Processar pacotes fora de ordem armazenados
            while self.seq_esperado in self.pacotes_fora_de_ordem:
                conteudo_fora = self.pacotes_fora_de_ordem.pop(self.seq_esperado)
                print(f"Processando pacote fora de ordem: {self.seq_esperado} - {conteudo_fora}")
                self.mensagens_recebidas[self.seq_esperado] = conteudo_fora
                self.enviar_ack(conn, self.seq_esperado)
                self.seq_esperado += 1
        elif seq_num > self.seq_esperado:
            # Pacote fora de ordem
            print(f"Pacote {seq_num} fora de ordem: {conteudo}. Esperado: {self.seq_esperado}")
            self.pacotes_fora_de_ordem[seq_num] = conteudo
            self.enviar_nak(conn, self.seq_esperado)
        else:
            # Pacote já recebido
            print(f"Pacote {seq_num} já recebido anteriormente: {conteudo}")
            self.enviar_ack(conn, seq_num)

    def receber_dados(self, conn):
        buffer = ""
        while True:
            try:
                data = conn.recv(1024).decode()
                if not data:
                    print("Cliente desconectado.")
                    break

                buffer += data
                while "\n" in buffer:
                    linha, buffer = buffer.split("\n", 1)
                    partes = linha.strip().split(":")
                    if len(partes) >= 4:
                        comando, seq_num_str, conteudo, checksum_recebido_str = partes
                        seq_num = int(seq_num_str)
                        checksum_recebido = int(checksum_recebido_str)

                        print(f"Recebido {comando}:{seq_num}:{conteudo} "
                              f"(Checksum recebido: {checksum_recebido})")

                        if comando == "SEND":
                            self.processar_pacote(conn, seq_num, conteudo, checksum_recebido)
                        elif comando == "ERR":
                            print(f"Pacote {seq_num} corrompido recebido (ERR): {conteudo}")
                            self.enviar_nak(conn, seq_num)
                    else:
                        print(f"Mensagem recebida em formato desconhecido: {linha.strip()}")
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
    host = input("Digite o endereço do servidor (127.0.0.1 por padrão): ") or "127.0.0.1"
    port = int(input("Digite a porta do servidor (12346 por padrão): ") or 12346)
    protocolo = input("Escolha o protocolo (SR para Selective Repeat, GBN para Go-Back-N): ").upper()
    cumulativo = input("Deseja confirmar pacotes cumulativamente? (S/N): ").lower() == "s"
    servidor = Servidor(host, port, protocolo, cumulativo)
    servidor.iniciar()

if __name__ == "__main__":
    menu_servidor()
