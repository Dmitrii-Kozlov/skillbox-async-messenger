import asyncio
from asyncio import transports
from typing import Optional
from asyncqt import QEventLoop
from app.client_ui import Ui_MainWindow
from PySide2.QtWidgets import QMainWindow, QApplication


class ClientProtocol(asyncio.Protocol):
    transport: transports.Transport
    window: 'Chat'

    def __init__(self, chat):
        self.window = chat

    def data_received(self, data: bytes):
        decoded = data.decode()
        self.window.plainTextEdit.appendPlainText(decoded)

    def connection_made(self, transport: transports.BaseTransport):
        self.window.plainTextEdit.appendPlainText("Connected to server, enter login:<your login>")
        self.transport = transport

    def connection_lost(self, exception):
        self.window.plainTextEdit.appendPlainText("Connection lost...")



class Chat(QMainWindow, Ui_MainWindow):
    protocol: ClientProtocol

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.pushButton.clicked.connect(self.send_message)

    def send_message(self):
        message = self.lineEdit.text()
        self.lineEdit.clear()
        self.protocol.transport.write(message.encode())

    def create_protocol(self):
        self.protocol = ClientProtocol(self)
        return self.protocol

    async def start(self):
        loop = asyncio.get_running_loop()
        self.show()
        courutine = loop.create_connection(
            self.create_protocol,
            "127.0.0.1",
            8000
        )
        await asyncio.wait_for(courutine, 1000)

app = QApplication()
loop = QEventLoop(app)
asyncio.set_event_loop(loop)
window = Chat()

loop.create_task(window.start())
loop.run_forever()
