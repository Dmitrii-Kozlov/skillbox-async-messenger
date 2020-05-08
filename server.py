import asyncio
from asyncio import transports
from typing import Optional


class ClientProtocol(asyncio.Protocol):
    login: str
    server: 'Server'
    transport: transports.Transport

    def __init__(self, server: 'Server'):
        self.server = server
        self.login = None

    def data_received(self, data: bytes):
        decoded = data.decode(errors="ignore")
        print(decoded)
        if self.login is None:
            if decoded.startswith('login:'):
                login = decoded.replace("login:", "").replace("\r\n", "")
                # проверка занятого логина
                if login in (log.login for log in self.server.clients):
                    self.transport.write(f"Login <{login}> is occupied. Try another one.\n".encode())
                    self.transport.close()
                # если логин не занят присваиваем его и отправляем последние десять сообщений из чата
                else:
                    self.login = login
                self.transport.write(
                    f"Hello {self.login}!\n".encode()
                )
                self.send_history()
        else:
            self.send_message(decoded)

    def send_message(self, message):
        format_string = f"<{self.login} > {message}"
        encoded = format_string.encode()
        # добавляем сообщение в "список из 10 сообщений" и проверяем, чтобы список не разростался
        if len(self.server.chat) >= 10:
            self.server.chat.pop(0)
        self.server.chat.append(encoded)

        for client in self.server.clients:
            if client.login != self.login:
                client.transport.write(encoded)

    def send_history(self):
        for old_chat in self.server.chat:
            self.transport.write(old_chat)

    def connection_made(self, transport: transports.Transport):
        self.transport = transport
        self.server.clients.append(self)
        print("connection made")

    def connection_lost(self, exception):
        self.server.clients.remove(self)
        print("connection lost")


class Server:
    clients: list
    # создаем список для хранения чата
    chat = []

    def __init__(self):
        self.clients = []

    def create_protocol(self):
        return ClientProtocol(self)

    async def start(self):
        loop = asyncio.get_running_loop()

        courutine = await loop.create_server(
            self.create_protocol,
            "127.0.0.1",
            8000
        )

        print('Server started...')

        await courutine.serve_forever()


process = Server()
try:
    asyncio.run(process.start())
except KeyboardInterrupt:
    print("manual stopped!")
