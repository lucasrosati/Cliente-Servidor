import socket
import threading

class Servidor:
    def __init__(self, host, port, protocolo, cumulativo, tamanho_janela):
        self.host = host
        self.port = port
        self.protocolo = protocolo  # 'SR' para Selective Repeat, 'GBN' para Go-Back-N
        self.cumulativo = cumulativo  # Confirmação cumulativa (True/False)
        self.tamanho_janela = tamanho_janela  # Tamanho da janela de recepção
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.host, self.port))
        self.socket.listen(5)
        self.seq_esperado = 1
        self.mensagens_recebidas = {}
        self.pacotes_fora_de_ordem = {}  # Armazena pacotes fora de ordem
        self.janela_recepcao = list(range(1, self.tamanho_janela + 1))  # Janela inicial

    def calcular_checksum(self, mensagem):
        return sum(ord(c) for c in mensagem) & 0xFFFF

    def atualizar_janela(self):
        """Atualiza a janela de recepção dinamicamente com base no próximo pacote esperado."""
        while self.seq_esperado in self.mensagens_recebidas:
            self.seq_esperado += 1
        self.janela_recepcao = list(range(self.seq_esperado, self.seq_esperado + self.tamanho_janela))
        print(f"Janela de recepção atualizada: {self.janela_recepcao}")

    def enviar_ack(self, conn, seq_num):
        ack_data = f"ACK:{seq_num}"
        checksum = self.calcular_checksum(ack_data)
        ack = f"{ack_data}:{checksum}\n"
        conn.sendall(ack.encode())
        print(f"Enviado: {ack.strip()}")

    def enviar_nak(self, conn, seq_num):
        nak_data = f"NAK:{seq_num}"
        checksum = self.calcular_checksum(nak_data)
        nak = f"{nak_data}:{checksum}\n"
        conn.sendall(nak.encode())
        print(f"Enviado: {nak.strip()}")

    def processar_pacote(self, conn, seq_num, conteudo, checksum_recebido):
        checksum_calculado = self.calcular_checksum(conteudo)

        if checksum_recebido != checksum_calculado:
            print(f"Erro de checksum no pacote {seq_num}: {conteudo}")
            if seq_num not in self.mensagens_recebidas:
                self.enviar_nak(conn, seq_num)
        elif seq_num == self.seq_esperado:
            print(f"Pacote {seq_num} confirmado: {conteudo}")
            self.mensagens_recebidas[seq_num] = conteudo
            self.enviar_ack(conn, seq_num)
            self.atualizar_janela()

            # Processar pacotes fora de ordem armazenados
            while self.seq_esperado in self.pacotes_fora_de_ordem:
                conteudo_fora = self.pacotes_fora_de_ordem.pop(self.seq_esperado)
                print(f"Processando pacote fora de ordem: {self.seq_esperado} - {conteudo_fora}")
                self.mensagens_recebidas[self.seq_esperado] = conteudo_fora
                self.enviar_ack(conn, self.seq_esperado)
                self.atualizar_janela()
        elif seq_num in self.janela_recepcao:
            print(f"Pacote {seq_num} fora de ordem: {conteudo}. Dentro da janela: {self.janela_recepcao}")
            self.pacotes_fora_de_ordem[seq_num] = conteudo
            self.enviar_nak(conn, self.seq_esperado)
        else:
            if seq_num < self.seq_esperado:
                print(f"Pacote {seq_num} já recebido anteriormente: {conteudo}")
                self.enviar_ack(conn, seq_num)
            else:
                print(f"Pacote {seq_num} fora da janela de recepção: {conteudo}. Esperado: {self.janela_recepcao}")
                self.enviar_nak(conn, seq_num)

    def extrair_handshake(self, handshake_msg):
        try:
            partes = handshake_msg.split(":")
            protocolo = partes[2]
            janela = partes[4]
            return protocolo.upper(), int(janela)
        except IndexError:
            print("Erro ao processar a mensagem de handshake.")
            return None, None



    def receber_dados(self, conn):
        buffer = ""

        # Validação do Handshake
        try:
            handshake_msg = conn.recv(1024).decode().strip()
            if handshake_msg.startswith("HANDSHAKE:"):
                print(f"Handshake recebido: {handshake_msg}")
                protocolo, janela = self.extrair_handshake(handshake_msg)

                if protocolo == self.protocolo and janela == self.tamanho_janela:
                    ack_handshake = f"ACK_HANDSHAKE:PROTOCOL:{self.protocolo}:WINDOW:{self.tamanho_janela}\n"
                    conn.sendall(ack_handshake.encode())
                    print(f"Handshake confirmado: {ack_handshake.strip()}")
                else:
                    print("Falha no handshake. Encerrando conexão.")
                    conn.close()
                    return
            else:
                print("Mensagem inválida no handshake. Encerrando conexão.")
                conn.close()
                return
        except Exception as e:
            print(f"Erro durante o handshake: {e}")
            conn.close()
            return

        # Processamento dos pacotes
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
            except ConnectionResetError:
                print("Cliente encerrou a conexão inesperadamente.")
                break
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
    tamanho_janela = int(input("Digite o tamanho da janela de recepção (ex.: 5): "))
    servidor = Servidor(host, port, protocolo, cumulativo, tamanho_janela)
    servidor.iniciar()

if __name__ == "__main__":
    menu_servidor()