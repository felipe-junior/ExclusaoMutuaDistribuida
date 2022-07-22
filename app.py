import asyncio
from websockets import server
from threading import Thread
import logging
from datetime import datetime


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

    return mensagem, processo, lixo


async def echo(websocket: server.WebSocketServerProtocol):
    fila = []
    # Toda vez que dermos um grant para um processo, temos que salvar seu id para contar e saber quantas vezes ele acessou. Ou algo parecido com isso, mas temos que saber quantas vezes cada processo acessou a região crítica através do terminal.
    async for message in websocket:

        mensagem, processo, lixo = desfazMensagem(message)
        logger.info(
            f'TIMESTAMP: {datetime.today()} TIPO DE MENSAGEM: {mensagem} NUMERO DO PROCESSO: {processo}')

        # Lógica do controle de fila tá zoado. To cheio de sono, rapaziada. Espero ter adiantado um pouco.
        if message.split('|')[0] == str(1):
            if len(fila) == 0:
                fila.append({'ID_Thread': message.split(
                    '|')[1], 'Socket': websocket})
                await websocket.send("GRANT")
            if len(fila) > 0:
                fila.append({'ID_Thread': message.split(
                    '|')[1], 'Socket': websocket})
        else:
            del fila[0]
            # Eu não sei se isso aqui ta sendo efetivo. Tentei sobrescrever o socket com o primeiro da fila toda vez que eu recebo um release. Para dar grant a outro processo. Mas n sei se essa desgraça tá funcionando.
            websocket = fila[0]['Socket']
            await websocket.send("GRANT")

        # Lógica da fila tá toda torta, conseguem ajeitar? Cheio de sono.


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
            print('Imprimindo fila')
        elif input_thread == 2:
            print('Imprimindo quantidade')
        elif input_thread == 3:
            print('Encerrando execução.')
            break
        else:
            continue


# Instanciando e iniciando a thread do terminal
thread_terminal = Thread(target=terminal)
thread_terminal.start()

# Instanciando e iniciando a thread do controle de fila
thread_controle_de_fila = Thread(target=controle_de_fila)
thread_controle_de_fila.start()

asyncio.run(main())
