
# Manual de Utilização

## Descrição Geral

Este projeto é uma aplicação cliente-servidor em Python, projetada para fornecer transporte confiável de dados em uma rede com perdas e erros simulados.

### Requisitos

- **Cliente**: Envia pacotes com números de sequência e espera confirmações (`ACK` ou `NAK`).
- **Servidor**: Recebe pacotes, envia confirmações e permite simulação de perda e erro nas mensagens.

## Configuração do Ambiente

1. Clone o repositório.
2. Verifique se possui Python 3.8 ou superior instalado.
3. Instale as dependências, se houver.

## Executando o Servidor

1. Navegue até o diretório `servidor`.
2. Execute o comando:

   ```bash
   python3 servidor.py
   ```

   O servidor começará a escutar na porta especificada.

## Executando o Cliente

1. Navegue até o diretório `cliente`.
2. Execute o comando:

   ```bash
   python3 cliente.py
   ```

   O cliente se conectará ao servidor e iniciará o envio de pacotes.

## Modos de Operação

- **Selective Repeat** e **Go-Back-N**: Alterne o modo no arquivo `servidor.py` alterando a variável `modo_retransmissao`.
- **Confirmação em Grupo**: Ative ou desative as confirmações em grupo usando `confirmacao_em_grupo` no `servidor.py`.

## Funcionalidades

1. **Simulação de Erros**: Falhas de integridade e perda de pacotes podem ser simuladas no lado cliente e servidor.
2. **Retransmissão**: Pacotes são retransmitidos pelo cliente após o timeout caso não receba um `ACK`.
3. **Controle de Fluxo e Janela Deslizante**: Implementação de janela deslizante e controle de fluxo para evitar congestionamento.
4. **Relatório de Status**: O cliente exibe o total de pacotes enviados e retransmitidos ao final da execução.
