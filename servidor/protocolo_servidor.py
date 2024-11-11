# protocolo_servidor.py
class ProtocoloServidor:
    def mensagem_enviar(self, tipo, numero_sequencia, conteudo=""):
        """
        Formata uma mensagem para envio ao cliente.
        """
        return f"{tipo}:{numero_sequencia}:{conteudo}"

    def mensagem_receber(self, mensagem):
        """
        Processa a mensagem recebida do cliente e retorna o tipo, número de sequência e conteúdo.
        """
        partes = mensagem.split(":")
        if len(partes) < 2:
            raise ValueError("Mensagem recebida em formato incorreto.")
        tipo = partes[0]
        numero_sequencia = int(partes[1])
        conteudo = partes[2] if len(partes) > 2 else ""
        return tipo, numero_sequencia, conteudo
