import socket
import time

from core.Module1_txt import input_plus, print_plus

HOST = "0.0.0.0"  # 服务端-本机
PORT = 50000        # 任意未占用端口

BUFFER_SIZE = 16384
DELAY = 0.3

class HeadTags:
    STR_TAG = "\tSTR\t"
    EXIT_TAG = "\tEXIT\t"
    ASK_TAG = "\tASK\t"
    TEST_TAG = "\tTEST\t"
    LONG_STR_TAG = "\tLONG\t"
    NONE_TAG = "\tNONE\t"

class Server:

    def __init__(self):
        # 服务器socket对象生成
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 会话socket对象生成
        self.connection_socket:socket = None
        # 地址数据注入
        self.server_socket.bind((HOST,PORT))

        self.buffer = ""

    def close(self):
        self.connection_socket.close()
        self.server_socket.close()

    def connect(self):
        # 开始监听
        self.server_socket.listen(1)
        print("服务端启动，等待客户端连接...")
        # 阻塞 直到连接到手
        self.connection_socket, addr = self.server_socket.accept()
        print(f"客户端已连接>{addr}")

    def test(self):
        start = time.time()
        self.connection_socket.send(HeadTags.TEST_TAG.encode("utf-8"))
        self.connection_socket.recv(BUFFER_SIZE).decode("utf-8")
        end = time.time()
        print(f"响应时间>{end-start:.2f}s")

    def send_str(self,msg:str):
        self.connection_socket.send(
            (HeadTags.STR_TAG+msg).encode("utf-8")
        )
        time.sleep(DELAY)

    def send_long_str(self,msg:str):
        self.connection_socket.send(
            (HeadTags.LONG_STR_TAG+msg).encode("utf-8")
        )
        time.sleep(DELAY)

    def ask(self,prompt:str) -> str:
        self.connection_socket.send(
            (HeadTags.ASK_TAG+prompt).encode("utf-8")
        )
        response = self.connection_socket.recv(BUFFER_SIZE).decode("utf-8")
        if response == HeadTags.NONE_TAG:
            response = ""
        return response
    
    def buffer_append(self,msg:str):
        self.buffer += msg
        self.buffer += "\n"

    def buffer_send(self):
        self.send_str(self.buffer)
        self.buffer = ""


    def send_exit(self,msg:str):
        self.connection_socket.send(HeadTags.EXIT_TAG.encode("utf-8")+msg.encode("utf-8"))

class Client:

    def __init__(self):
        # 客户端socket对象生成
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 会话socket对象生成
        self.connection_socket:socket = None

    def close(self):
        self.client_socket.close()

    def connect(self):
        server_host = input_plus("请输入长机设备的局域网地址>>>")
        self.client_socket.connect((server_host, PORT))

    def start_main_loop(self):
        print_plus("主循环启动……正在接收服务器提问")
        while 1:
            prompt = self.client_socket.recv(BUFFER_SIZE).decode("utf-8")
            parts = prompt.split("\t", 2)  # 最多分割成3部分
            if len(parts) < 3:
                continue
            tag = "\t" + parts[1] + "\t"
            content = parts[2]
            match tag:
                case HeadTags.STR_TAG:
                    print_plus(content)
                case HeadTags.LONG_STR_TAG:
                    for line in content.splitlines():
                        print(line)
                case HeadTags.EXIT_TAG:
                    print_plus(content)
                    break
                case HeadTags.ASK_TAG:
                    answer = input_plus(content)
                    if answer == "":
                        answer = HeadTags.NONE_TAG
                    self.client_socket.send(answer.encode("utf-8"))
                case HeadTags.TEST_TAG:
                    self.client_socket.send(b"test")
                case _:
                    pass
        print_plus("主循环结束")
        self.client_socket.close()