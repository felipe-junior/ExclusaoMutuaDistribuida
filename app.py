import asyncio
from websockets import server
from threading import Thread
import logging
from datetime import datetime
import numpy as np

logging.basicConfig(filename='controlador.log',
                    # w -> sobrescreve o arquivo a cada log
                    # a -> não sobrescreve o arquivo
                    filemode='a',
                    level=logging.INFO)
logger = logging.getLogger('root')


def desfazMensagem(message):
    mensagem, processo, lixo = message.split('|')
    if mensagem == '1':
        mensagem = 'REQUEST'
    else:
        mensagem = 'RELEASE'

    return mensagem, processo


fila = []
qtd = np.zeros(20)


async def echo(websocket: server.WebSocketServerProtocol):
    # Toda vez que dermos um grant para um processo, temos que salvar seu id para contar e saber quantas vezes ele acessou. Ou algo parecido com isso, mas temos que saber quantas vezes cada processo acessou a região crítica através do terminal.
    async for message in websocket:

        mensagem, processo = desfazMensagem(message)
        logger.info(
            f'TIMESTAMP: {datetime.today()} TIPO DE MENSAGEM: {mensagem} NUMERO DO PROCESSO: {processo}')

        # Lógica do controle de fila tá zoado. To cheio de sono, rapaziada. Espero ter adiantado um pouco.
        if mensagem == 'REQUEST':
            if len(fila) == 0:
                fila.append({'websocket': websocket, 'processo': processo})
                await fila[0]['websocket'].send('GRANT')
                filaProcesso = fila[0]['processo']
                logger.info(
                    f'TIMESTAMP: {datetime.today()} TIPO DE MENSAGEM: GRANT NUMERO DO PROCESSO: {filaProcesso}')
                qtd[int(filaProcesso)] = qtd[int(filaProcesso)] + 1
            else:
                fila.append({'websocket': websocket, 'processo': processo})
        elif mensagem == 'RELEASE':
            fila.pop(0)
            if len(fila) != 0:
                await fila[0]['websocket'].send('GRANT')
                filaProcesso = fila[0]['processo']
                logger.info(
                    f'TIMESTAMP: {datetime.today()} TIPO DE MENSAGEM: GRANT NUMERO DO PROCESSO: {filaProcesso}')
                qtd[int(filaProcesso)] = qtd[int(filaProcesso)] + 1


async def main():
    async with server.serve(echo, "localhost", 8765):
        await asyncio.Future()  # run forever

# Thread para o controle de fila, não soube fazer, como dito acima


def controle_de_fila():
    print('Algum controle de fila aqui nessa thread. Codar')

# Aqui é uma thread para o terminal, depende do código do controle de fila para impressão da fila e da quantidade de vezes que determinada thread acessou a região crítica. Mas a lógica segue essa aí.


def terminal():
    while True:
        input_thread = int(input(
            'O que você precisa?\n1. Imprimir fila de pedidos atual\n2. Imprimir quantas vezes cada processo foi atendido\n3. Encerrar execução\n'))
        if input_thread == 1:
            print(fila)
        elif input_thread == 2:
            for i in range(len(qtd)):
                print(f'Processo {i}: {qtd[i]}')
        elif input_thread == 3:
            print('Encerrando execução.')
            break
        else:
            continue


# Instanciando e iniciando a thread do terminal
thread_terminal = Thread(target=terminal)
thread_terminal.start()

# Instanciando e iniciando a thread do controle de fila
#thread_controle_de_fila = Thread(target=controle_de_fila)
# thread_controle_de_fila.start()

asyncio.run(main())
