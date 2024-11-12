# protocolo_cliente.py
class ProtocoloCliente:
    def criar_pacote(self, tipo, seq_num, conteudo):
        return f"{tipo}:{seq_num}:{conteudo}"

    def extrair_dados(self, mensagem):
        partes = mensagem.split(":")
        if len(partes) >= 3:
            return partes[0], int(partes[1]), partes[2]
        else:
            raise ValueError("Pacote mal formatado")