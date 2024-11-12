
# Aplicação Cliente-Servidor com Controle de Fluxo e Retransmissão

## Descrição

Este projeto é uma aplicação cliente-servidor em Python que implementa um protocolo de comunicação confiável na camada de aplicação, considerando um canal de comunicação com perdas e erros simulados. A aplicação utiliza um sistema de janela deslizante para controle de fluxo e congestionamento, além de temporizadores para garantir a retransmissão de pacotes perdidos.

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
├── cliente/
│   ├── cliente.py                # Código principal do cliente
│   ├── protocolo_cliente.py       # Definição do protocolo do cliente
│   ├── simulador_erros.py         # Simulação de erros para o cliente
│   └── utils.py                   # Funções auxiliares para o cliente (checksum, temporizadores, etc.)
├── servidor/
│   ├── servidor.py                # Código principal do servidor
│   ├── protocolo_servidor.py      # Definição do protocolo do servidor
│   ├── simulador_erros.py         # Simulação de erros para o servidor
│   └── utils.py                   # Funções auxiliares para o servidor (controle de fluxo, etc.)
├── docs/
│   ├── manual_utilizacao.md       # Manual de utilização do projeto
│   ├── relatorio_projeto.md       # Relatório detalhado do projeto
│   └── protocolo.md               # Descrição detalhada do protocolo de aplicação
├── testes/
│   ├── testes_cliente.py          # Testes para o cliente
│   ├── testes_servidor.py         # Testes para o servidor
│   └── mock_server.py             # Mock do servidor para testes locais do cliente
└── README.md                      # Este README com instruções detalhadas
```

## Requisitos

- Python 3.8 ou superior
- Bibliotecas padrão do Python

## Como Executar o Projeto

### Passo 1: Clonar o Repositório

Clone o repositório para o seu ambiente local:

```bash
git clone https://github.com/username/repo.git
cd repo
```

### Passo 2: Executar o Servidor

No terminal, navegue até o diretório do servidor e execute o servidor:

```bash
cd servidor
python3 servidor.py
```

O servidor estará agora em modo de escuta aguardando conexões de clientes.

### Passo 3: Executar o Cliente

Em outro terminal, navegue até o diretório do cliente e execute o cliente:

```bash
cd cliente
python3 cliente.py
```

O cliente tentará se conectar ao servidor e começará a enviar pacotes conforme configurado. Ele também mostrará um relatório de status no final da execução.

## Modos de Operação

O servidor pode operar em dois modos de controle de retransmissão:

- **Go-Back-N**: O servidor só aceita pacotes na sequência exata e solicita a retransmissão de pacotes fora de ordem.
- **Selective Repeat (Repetição Seletiva)**: O servidor aceita pacotes fora de ordem e confirma cada pacote individualmente, permitindo maior flexibilidade.

Para alternar entre os modos, altere a variável `modo_retransmissao` no arquivo `servidor.py`.

## Detalhes Técnicos

### Protocolo de Comunicação

- **Número de Sequência**: Cada pacote enviado inclui um número de sequência para controle de ordem.
- **ACK e NAK**: O servidor responde com `ACK` para pacotes recebidos corretamente e `NAK` para pacotes fora de ordem (no modo Go-Back-N).
- **Janela Deslizante**: O cliente envia múltiplos pacotes dentro de uma janela, esperando `ACKs` antes de avançar na sequência.
- **Simulação de Perda e Erro**: Funções de simulação de erros inserem falhas em pacotes e confirmações, permitindo o teste do comportamento em canais de comunicação com falhas.

### Relatório de Status

No final da execução, o cliente exibe um relatório com:
- **Pacotes enviados**: Número total de pacotes enviados ao servidor.
- **Pacotes retransmitidos**: Número de pacotes que foram retransmitidos devido a perda ou falha de confirmação.

## Exemplo de Execução

### Exemplo de Saída do Cliente

```plaintext
Conectado ao servidor em 127.0.0.1:12346
Enviado para o servidor: SEND:0:Pacote 0
Resposta do servidor: Tipo=ACK, Número de Sequência=0, Conteúdo=
Pacote 1 simulado como perdido.
Enviado para o servidor: SEND:2:Pacote 2
Resposta do servidor: Tipo=ACK, Número de Sequência=2, Conteúdo=
Enviado para o servidor: SEND:3:Pacote 3
Resposta do servidor: Tipo=ACK, Número de Sequência=3, Conteúdo=
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
Enviado para o cliente: ACK:0:
Recebido do cliente: SEND:2:Pacote 2
Enviado para o cliente: ACK:2:
Recebido do cliente: SEND:3:Pacote 3
Enviado para o cliente: ACK:3:
Recebido do cliente: SEND:1:Pacote 1
Simulando perda de ACK. Nenhuma confirmação enviada.
```

## Contribuição

Contribuições são bem-vindas! Se você deseja melhorar o projeto, sinta-se à vontade para abrir uma *pull request* ou relatar problemas na seção de *issues*.

## Licença

Este projeto está licenciado sob a Licença MIT - consulte o arquivo [LICENSE](LICENSE) para mais detalhes.
