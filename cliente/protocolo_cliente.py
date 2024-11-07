# cliente/protocolo_cliente.py

class ProtocoloCliente:
    def __init__(self):
        self.mensagens = {
            "SEND": "SEND",
            "SEND_BURST": "SEND_BURST",
            "ERROR": "ERROR",
            "END": "END"
        }

    def mensagem_enviar(self, tipo, conteudo="", numero_sequencia=0):
        """
        Retorna uma mensagem formatada para envio ao servidor, incluindo número de sequência.
        """
        if tipo in self.mensagens:
            return f"{self.mensagens[tipo]}:{numero_sequencia}:{conteudo}"
        else:
            raise ValueError("Tipo de mensagem não suportado")

    def mensagem_receber(self, mensagem):
        """
        Processa a mensagem recebida do servidor e retorna o tipo, número de sequência e conteúdo.
        """
        partes = mensagem.split(":")
        tipo = partes[0]

        # Verifica se o número de sequência é um valor numérico
        try:
            numero_sequencia = int(partes[1])
        except ValueError:
            print(f"Aviso: número de sequência inválido na mensagem recebida: {partes[1]}")
            return tipo, None, partes[2] if len(partes) > 2 else ""

        conteudo = partes[2] if len(partes) > 2 else ""
        return tipo, numero_sequencia, conteudo
