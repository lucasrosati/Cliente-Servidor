# servidor/protocolo_servidor.py

class ProtocoloServidor:
    def __init__(self):
        self.respostas = {
            "ACK": "ACK",
            "NAK": "NAK",
            "ACK_BATCH": "ACK_BATCH"
        }

    def resposta_enviar(self, tipo, numero_sequencia=0, conteudo=""):
        """
        Retorna uma resposta formatada para envio ao cliente, incluindo número de sequência.
        """
        if tipo in self.respostas:
            return f"{self.respostas[tipo]}:{numero_sequencia}:{conteudo}"
        else:
            raise ValueError("Tipo de resposta não suportado")

    def resposta_receber(self, resposta):
        """
        Processa a resposta recebida do cliente e retorna o tipo, número de sequência e conteúdo.
        """
        partes = resposta.split(":")
        tipo = partes[0]
        numero_sequencia = int(partes[1])
        conteudo = partes[2] if len(partes) > 2 else ""
        return tipo, numero_sequencia, conteudo
