
# Relatório do Projeto Cliente-Servidor

## Descrição do Protocolo de Aplicação

Este documento descreve o protocolo de aplicação utilizado na comunicação entre o cliente e o servidor.

### Tipos de Mensagem

#### 1. Mensagem de Envio (SEND)
- **Formato**: `SEND:<número_sequência>:<conteúdo>`
- **Descrição**: O cliente usa essa mensagem para enviar dados para o servidor. O `<número_sequência>` identifica a ordem do pacote, e `<conteúdo>` contém a mensagem real.
- **Exemplo**: `SEND:1:Honda`

#### 2. Confirmação Positiva (ACK)
- **Formato**: `ACK:<número_sequência>:<conteúdo>`
- **Descrição**: O servidor envia um `ACK` para confirmar a recepção correta de um pacote. O `<número_sequência>` indica o número de sequência do pacote confirmado, e `<conteúdo>` é opcional.
- **Exemplo**: `ACK:1`

#### 3. Confirmação Negativa (NAK)
- **Formato**: `NAK:<número_sequência>:<conteúdo>`
- **Descrição**: O servidor usa um `NAK` para informar que um pacote específico não foi recebido ou está fora de ordem. O `<número_sequência>` indica o número do pacote que deve ser retransmitido.
- **Exemplo**: `NAK:2`

## Simulação de Erros

1. **Erro de Integridade**: A integridade do pacote é verificada usando um checksum. Se o checksum calculado não corresponder ao checksum enviado, o pacote será descartado, e um NAK será enviado de volta para o cliente.
2. **Perda de Pacotes**: A aplicação simula perda de pacotes, omitindo a resposta `ACK` ou `NAK` para um pacote, o que força o cliente a retransmitir após o timeout.
3. **Simulação de Erro nos ACKs**: O servidor pode enviar um ACK corrompido para simular falhas de comunicação.

## Confirmação em Grupo

O servidor pode enviar um `ACK` em grupo para confirmar múltiplos pacotes de uma vez. Exemplo: `ACK:1-5` confirma que os pacotes de sequência `1` a `5` foram recebidos com sucesso.

## Como o Cliente e o Servidor Funcionam

- O cliente envia pacotes com números de sequência para o servidor, esperando um `ACK` ou `NAK` como resposta.
- Quando o servidor recebe um pacote, ele verifica a integridade do pacote, processa a confirmação de acordo com a sequência recebida e, se necessário, armazena pacotes fora de ordem (quando o modo de retransmissão for **Selective Repeat**).
- Se o pacote for corrompido (erro de checksum) ou fora de ordem, o servidor retorna um `NAK` ou um `ACK` em grupo.
- Caso o cliente não receba um `ACK` para um pacote dentro do tempo limite, o pacote será retransmitido, com um mecanismo de controle de congestionamento utilizando a janela deslizante e um algoritmo de controle como **Slow Start** e **Congestion Avoidance**.

## Logs do Sistema

O sistema registra as operações, como o envio de pacotes, os `ACK`/`NAK` recebidos, os pacotes retransmitidos, e também os erros de integridade e perdas de pacotes. Exemplo de log:

### Exemplo de Logs do Servidor:
\`\`\`plaintext
Recebido SEND:1:Honda (Checksum recebido: 14968, Checksum calculado: 14968)
Enviado: ACK:1:7812 (Checksum: 7812)
Recebido SEND:2:Ferrari (Checksum recebido: 18651, Checksum calculado: 18651)
Enviado: ACK:2:7815 (Checksum: 7815)
Recebido ERR:5:telorvehC (Checksum recebido: 32632, Checksum calculado: 60040)
Erro de checksum no pacote 5
Enviado: NAK:5:4613 (Checksum: 4613)
Recebido ACK para pacote 5
\`\`\`

### Exemplo de Logs do Cliente:
\`\`\`plaintext
Enviado: SEND:1:Honda:14968
Enviado: SEND:2:Ferrari:18651
Enviado: SEND:3:Toyota:17366
Enviado: ERR:5:telorvehC:32632
Recebido ACK para pacote 1
Enviado ACK_CONFIRM para pacote 1 (Checksum: 2151)
Recebido NAK para pacote 5, retransmitindo...
Timeout para pacote 5, retransmitindo...
Enviado: SEND:5:Chevrolet:32632
Recebido ACK para pacote 5
\`\`\`

## Conclusão

O protocolo implementado permite uma comunicação robusta e eficiente entre o cliente e o servidor, com verificação de integridade, controle de fluxo e retransmissões. O sistema foi projetado para simular condições adversas de rede, como perda de pacotes e erros de checksum, para testar a confiabilidade do transporte de dados.
