
# Aplicação Cliente-Servidor com Controle de Fluxo e Retransmissão

## Descrição

Este projeto é uma aplicação cliente-servidor em Python que implementa um protocolo de comunicação confiável na camada de aplicação. Ele considera um canal de comunicação com perdas e erros simulados. A aplicação utiliza um sistema de janela deslizante para controle de fluxo e congestionamento, além de temporizadores para garantir a retransmissão de pacotes perdidos.

O servidor suporta dois modos de controle de retransmissão: **Go-Back-N** e **Selective Repeat** (Repetição Seletiva), permitindo maior flexibilidade e adaptação a diferentes condições de rede.

## Funcionalidades

- **Transporte Confiável de Dados**: Implementa um protocolo com confirmação de pacotes, números de sequência, retransmissão de pacotes e simulação de perdas e erros.
- **Janela Deslizante**: Controle de fluxo utilizando uma janela deslizante para gerenciar o envio e recebimento de pacotes.
- **Temporizador de Retransmissão**: Retransmissão automática de pacotes não confirmados dentro do tempo limite especificado.
- **Modos de Operação**: Suporte aos modos Go-Back-N e Selective Repeat para controle de retransmissão.
- **Simulação de Erros**: Inserção de erros em pacotes e confirmações para simular um canal de comunicação com falhas.

## Estrutura do Projeto

```plaintext
projeto_cliente_servidor/
├── cliente.py                # Código principal do cliente
├── servidor.py               # Código principal do servidor
└── carros.txt                # Arquivo com dados a serem enviados
```

## Requisitos

- Python 3.8 ou superior
- Nenhuma biblioteca adicional é necessária.

## Como Executar o Projeto

### Passo 1: Clonar o Repositório

Clone o repositório para o seu ambiente local:

```bash
git clone https://github.com/username/repo.git
cd projeto_cliente_servidor
```

### Passo 2: Executar o Servidor

No terminal, execute o servidor:

```bash
python3 servidor.py
```

O servidor estará agora em modo de escuta aguardando conexões de clientes.

### Passo 3: Executar o Cliente

Em outro terminal, execute o cliente:

```bash
python3 cliente.py
```

O cliente tentará se conectar ao servidor e começará a enviar pacotes conforme configurado. Ele também mostrará um relatório de status no final da execução.

## Modos de Operação

O servidor pode operar em dois modos de controle de retransmissão:

- **Go-Back-N**: O servidor só aceita pacotes na sequência exata e solicita a retransmissão de pacotes fora de ordem.
- **Selective Repeat (Repetição Seletiva)**: O servidor aceita pacotes fora de ordem e confirma cada pacote individualmente, permitindo maior flexibilidade.

Para alternar entre os modos, configure o protocolo no início da execução do servidor e do cliente.

## Detalhes Técnicos

### Protocolo de Comunicação

- **Número de Sequência**: Cada pacote enviado inclui um número de sequência para controle de ordem.
- **ACK e NAK**: O servidor responde com `ACK` para pacotes recebidos corretamente e `NAK` para pacotes fora de ordem (no modo Go-Back-N).
- **Janela Deslizante**: O cliente envia múltiplos pacotes dentro de uma janela, esperando `ACKs` antes de avançar na sequência.
- **Simulação de Perda e Erro**: Funções de simulação de erros inserem falhas em pacotes e confirmações, permitindo o teste do comportamento em canais de comunicação com falhas.

### Checksum

O checksum é calculado somando os valores ASCII de cada caractere da mensagem e aplicando a operação bitwise `& 0xFFFF` para limitar o valor a 16 bits. Ele é usado para verificar a integridade da mensagem. Se o checksum calculado não corresponder ao checksum recebido, o pacote será considerado corrompido e será solicitado um `NAK`.

### Verificação de tamanho da mensagem

O servidor verifica o tamanho do conteúdo de cada pacote recebido. Se o pacote exceder o tamanho permitido (self.tamanhoBuffer), o servidor exibe uma mensagem de aviso no console, indicando que o pacote ultrapassou o tamanho permitido e envia uma mensagem de erro para o cliente, composta pelo tipo de erro (ERRO_TAMANHO) e o número de sequência do pacote problemático. O checksum é calculado para garantir a integridade desta mensagem de erro.

### Relatório de Status

No final da execução, o cliente exibe um relatório com:
- **Pacotes enviados**: Número total de pacotes enviados ao servidor.
- **Pacotes retransmitidos**: Número de pacotes que foram retransmitidos devido a perda ou falha de confirmação.

## Exemplo de Execução

### Exemplo de Saída do Cliente

```plaintext
Conectado ao servidor em 127.0.0.1:12346
Enviado para o servidor: SEND:0:Pacote 0
Resposta do servidor: Tipo=ACK, Número de Sequência=0
Pacote 1 simulado como perdido.
Enviado para o servidor: SEND:2:Pacote 2
Resposta do servidor: Tipo=ACK, Número de Sequência=2
Enviado para o servidor: SEND:3:Pacote 3
Resposta do servidor: Tipo=ACK, Número de Sequência=3
Retransmitindo pacote 1 devido ao timeout.
Relatório de Status:
Pacotes enviados: 4
Pacotes retransmitidos: 1
```

### Exemplo de Saída do Servidor

```plaintext
Servidor iniciado em 127.0.0.1:12346 no modo Selective Repeat
Conexão estabelecida com ('127.0.0.1', 61978)
Recebido do cliente: SEND:0:Pacote 0
Enviado para o cliente: ACK:0
Recebido do cliente: SEND:2:Pacote 2
Enviado para o cliente: ACK:2
Recebido do cliente: SEND:3:Pacote 3
Enviado para o cliente: ACK:3
Recebido do cliente: SEND:1:Pacote 1
Simulando perda de ACK. Nenhuma confirmação enviada.
```

## Licença

Este projeto está licenciado sob a Licença MIT. Consulte o arquivo [LICENSE](LICENSE) para mais detalhes.
