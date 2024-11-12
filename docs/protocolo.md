
# Protocolo de Comunicação para Aplicação Cliente-Servidor

Este documento descreve o protocolo de aplicação utilizado na comunicação entre o cliente e o servidor.

## Tipos de Mensagem

### 1. Mensagem de Envio (SEND)
- **Formato**: `SEND:<número_sequência>:<conteúdo>`
- **Descrição**: O cliente usa essa mensagem para enviar dados para o servidor. O `<número_sequência>` identifica a ordem do pacote, e `<conteúdo>` contém a mensagem real.
- **Exemplo**: `SEND:1:Hello`

### 2. Confirmação Positiva (ACK)
- **Formato**: `ACK:<número_sequência>:<conteúdo>`
- **Descrição**: O servidor envia um `ACK` para confirmar a recepção correta de um pacote. O `<número_sequência>` indica o número de sequência do pacote confirmado, e `<conteúdo>` é opcional.
- **Exemplo**: `ACK:1`

### 3. Confirmação Negativa (NAK)
- **Formato**: `NAK:<número_sequência>:<conteúdo>`
- **Descrição**: O servidor usa um `NAK` para informar que um pacote específico não foi recebido ou está fora de ordem. O `<número_sequência>` indica o número do pacote que deve ser retransmitido.
- **Exemplo**: `NAK:2`

## Simulação de Erros

1. **Erro de Integridade**: A integridade do pacote é verificada usando um checksum.
2. **Perda de Pacotes**: A aplicação simula perda de pacotes, omitindo a resposta `ACK` ou `NAK` para um pacote, forçando o cliente a retransmitir após o timeout.

## Confirmação em Grupo

O servidor pode enviar um `ACK` em grupo para confirmar múltiplos pacotes de uma vez. Exemplo: `ACK:1-5` confirma que os pacotes de sequência `1` a `5` foram recebidos com sucesso.
