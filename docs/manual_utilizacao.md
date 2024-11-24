
# Manual de Utilização

## Descrição Geral

Este projeto é uma aplicação cliente-servidor em Python, projetada para fornecer transporte confiável de dados em uma rede com perdas e erros simulados. O protocolo de comunicação implementado garante a confiabilidade do transporte com a utilização de pacotes numerados, checksums para validação de integridade, e controle de fluxo através de janelas deslizantes.

### Requisitos

- **Cliente**: Envia pacotes com números de sequência e espera confirmações (`ACK` ou `NAK`). O cliente também implementa um controle de retransmissão e ajuste dinâmico de congestionamento.
- **Servidor**: Recebe pacotes, envia confirmações e permite simulação de perda e erro nas mensagens. O servidor também possui controle de janela de recepção e validação de pacotes recebidos.

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

   O servidor começará a escutar na porta especificada e estará pronto para receber conexões de clientes.

## Executando o Cliente

1. Navegue até o diretório `cliente`.
2. Execute o comando:

   ```bash
   python3 cliente.py
   ```

   O cliente se conectará ao servidor e iniciará o envio de pacotes. Durante a execução, o cliente irá exibir o total de pacotes enviados e retransmitidos ao final do processo.

## Modos de Operação

- **Selective Repeat (SR)**: O servidor aceita pacotes fora de ordem e envia um `ACK` para cada pacote recebido corretamente.
- **Go-Back-N (GBN)**: O servidor só aceita pacotes na sequência correta e solicita a retransmissão de pacotes fora de ordem.

Para alterar o modo de operação, modifique a variável `protocolo` no arquivo `servidor.py` para `'sr'` ou `'gbn'`.

## Funcionalidades

1. **Simulação de Erros**: 
   - **Erro de Integridade**: A integridade dos pacotes e confirmações é verificada utilizando checksum. Se o checksum não bater, o servidor ou cliente irá enviar um `NAK` (ou `ACK` para pacotes duplicados).
   - **Perda de Pacotes**: O cliente e o servidor podem simular a perda de pacotes aleatoriamente com base na probabilidade configurada. Pacotes perdidos são retransmitidos após um tempo de espera.
   
2. **Retransmissão**:
   - Pacotes são retransmitidos pelo cliente após um `timeout` caso o cliente não receba um `ACK` para o pacote enviado. O número máximo de tentativas para retransmissão pode ser configurado.

3. **Controle de Fluxo e Janela Deslizante**:
   - **Janela Deslizante**: O cliente utiliza uma janela de envio que permite enviar múltiplos pacotes sem esperar um `ACK` para cada um. A janela é ajustada dinamicamente com base no congestionamento.
   - **Controle de Janela no Servidor**: O servidor ajusta dinamicamente a janela de recepção e informa o tamanho atual ao cliente em cada `ACK` ou `NAK`.

4. **Envio em Rajada**:
   - **Cliente**: Serializa vários pacotes em uma única mensagem separada por `;` e envia como um bloco.
   - **Servidor**: Processa a rajada, verifica integridade e sequência de cada pacote dentro dela, descarta pacotes fora da janela e confirma os válidos.
   - **Nota**: Caso o cliente envie mais pacotes do que o tamanho atual da janela do servidor, os pacotes excedentes serão descartados.

5. **Relatório de Status**:
   - O cliente exibe ao final da execução um relatório com o número total de pacotes enviados e o número de pacotes retransmitidos devido a erros ou perdas.

6. **Confirmação em Grupo**:
   - O servidor pode enviar um `ACK` em grupo para confirmar múltiplos pacotes de uma vez. Por exemplo: `ACK:1-5` confirma que os pacotes de sequência `1` a `5` foram recebidos corretamente.

7. **Controle de Retransmissão**:
   - O cliente utiliza um temporizador para controlar a retransmissão dos pacotes que não foram confirmados dentro do tempo especificado. Caso ocorra uma falha na confirmação de um pacote, ele será retransmitido automaticamente.

## Exemplo de Execução

### Exemplo de Saída do Cliente

```plaintext
Conectado ao servidor em 127.0.0.1:12346
Enviado em rajada: SEND:1:Honda:14968;SEND:2:Ferrari:18651;SEND:3:Toyota:17366
Recebido ACK para pacote 1
Recebido ACK para pacote 2
Recebido ACK para pacote 3
Simulando perda do pacote 5
Timeout para pacote 5, retransmitindo...
Relatório de Status:
Pacotes enviados: 6
Pacotes retransmitidos: 1
```

### Exemplo de Saída do Servidor

```plaintext
Servidor iniciado em 127.0.0.1:12346 no modo Selective Repeat
Conexão estabelecida com ('127.0.0.1', 61978)
Recebida rajada de pacotes: SEND:1:Honda;SEND:2:Ferrari;SEND:3:Toyota
Pacote 1 confirmado
Pacote 2 confirmado
Pacote 3 confirmado
Enviado: ACK:3:WINDOW:5
```

## Contribuição

Contribuições são bem-vindas! Se você deseja melhorar o projeto, sinta-se à vontade para abrir uma *pull request* ou relatar problemas na seção de *issues*.

## Licença

Este projeto está licenciado sob a Licença MIT - consulte o arquivo [LICENSE](LICENSE) para mais detalhes.
