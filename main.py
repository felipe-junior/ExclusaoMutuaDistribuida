import asyncio
from websockets import client
import multiprocessing
import time
from datetime import datetime

# Definindo os ids dos comandos abaixo
request = 1
release = 2
# Setando o tamanho da string
F = 10
# Número de vezes que o processo vai solicitar para entrar na região crítica
r = 5
# Tempo em segundos que o processo vai dormir após entrar na região crítica
k = 3

# Função que retorna a mensagem no formato desejado com separadores, indentificadores de Thread e Comando


def retornaMensagemFormatada(type, id):
    string = str(type) + '|' + str(id) + '|'
    tamanho_mensagem = len(string)
    if tamanho_mensagem < 10:
        string = string + (10 - tamanho_mensagem) * '0'
    return string


def createClient(id):
    async def hello():
        async with client.connect("ws://localhost:8765") as websocket:
            for i in range(r):
                # Chamando a função para formatar a mensagem, passando o comando e o id da thread.
                mensagem = retornaMensagemFormatada(request, id)
                await websocket.send(mensagem)
                try:
                    # Aguardando receber o GRANT do controlador
                    await websocket.recv()
                    # Registrando o id do processo e o timestamp
                    with open('resultado.txt', 'a') as res:
                        res.write(
                            f'Processo {id} - Timestamp: {datetime.today()}\n')
                    # Sleep no código só para fins de "fiz alguma coisa e saí"
                    time.sleep(k)
                    # Retorna a mensagem de release para o controlador
                    mensagem = retornaMensagemFormatada(release, id)
                    await websocket.send(mensagem)
                except client.ClientConnection.close_expected:
                    print(f'Terminated')
                    break
    asyncio.run(hello())


# Instanciando os PROCESSOS 1 e 2

if __name__ == "__main__":
    p1 = multiprocessing.Process(target=createClient, args=(1,))
    p2 = multiprocessing.Process(target=createClient, args=(2,))
    p3 = multiprocessing.Process(target=createClient, args=(3,))

    p1.start()
    p2.start()
    p3.start()
