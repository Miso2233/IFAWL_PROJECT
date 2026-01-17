import socket
import time

from core.Module0_enums_exceptions import IFAWL_ConnectionCancel
from core.Module1_txt import input_plus, print_plus,Tree,qte

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
    QTE_TAG = "\tQTE\t"

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
        #self.server_socket.setblocking(False)
        #self.connection_socket.setblocking(False)
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

    def send_tree(self,tree:Tree):
        self.send_long_str(
            "\n".join(tree.generate_line_list())+"\n"
        )

    def ask(self,prompt:str) -> str:
        #self.connection_socket.setblocking(True)
        self.connection_socket.send(
            (HeadTags.ASK_TAG+prompt).encode("utf-8")
        )
        response = self.connection_socket.recv(BUFFER_SIZE).decode("utf-8")
        if response == HeadTags.NONE_TAG:
            response = ""
        #self.connection_socket.setblocking(False)
        return response

    def ask_plus(self,txt: str, kword: list):
        kword_str = kword.copy()
        kword_str = [str(j) for j in kword]
        while 1:
            response = self.ask(txt)
            if response in kword_str:
                break
            else:
                self.send_str("请在可选范围内输入")
        return response

    def send_qte(self,who:str, perfect_txt="!FIRE!", good_txt="SPLASH!!") -> int:
        """
        发送qte
        :param who: 发起者
        :param perfect_txt: perfect文本
        :param good_txt: good文本
        :return: qte结算
        """
        self.connection_socket.send(
            f"{HeadTags.QTE_TAG}{who}\n{perfect_txt}\n{good_txt}".encode("utf-8")
        )
        response = self.connection_socket.recv(BUFFER_SIZE).decode("utf-8")
        return int(response)

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
        while 1:
            try:
                server_host = input_plus("请输入长机设备的局域网地址|[space]回环地址|[enter]退出>>>")
                if server_host == "":
                    raise IFAWL_ConnectionCancel
                elif server_host == " ":
                    server_host = "127.0.0.1"
                self.client_socket.connect((server_host, PORT))
            except ConnectionRefusedError:
                print_plus("连接失败，请检查长机设备是否已启动")
            except socket.timeout:
                print_plus("连接超时，请检查网络连接或稍后重试")
            except socket.gaierror:
                print_plus("地址无效，请检查输入的IP地址是否正确")
            except OSError as e:
                print_plus(f"网络错误: {str(e)}")
            except IFAWL_ConnectionCancel:
                raise
            else:
                break


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
                case HeadTags.QTE_TAG:
                    who, perfect_txt, good_txt = content.split("\n")
                    result = qte(who, perfect_txt, good_txt)
                    self.client_socket.send(str(result).encode("utf-8"))
                case _:
                    pass
        print_plus("主循环结束")
        self.client_socket.close()