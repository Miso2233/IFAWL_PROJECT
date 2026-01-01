from core.Module1_txt import print_plus, input_plus


class Auto_pilot_manager:#自动驾驶

    def __init__(self):
        self.to_do_list_normal  = [] # 在condition为真时执行的操作
        self.to_do_list_special = [] # 在condition为假时执行的操作
        self.condition_list     = [] # 记载condition的表格
        self.memory=[]

    def read(self,txt:str):
        """
        读取并分析AP代码
        :param txt: AP代码
        :return: 无
        """
        # 代码预处理
        txt=txt.replace("(","(-")
        txt=txt.replace("])","]);p") # 把循环判定解释为条件语句。去往")"之后去"("，还是去往"p"之后去下一操作
        # 清空三大列表
        self.to_do_list_normal  = []
        self.to_do_list_special = []
        self.condition_list     = []
        # 按照减号分割token
        raw_token_list = txt.split("-")     #["2","2","[True]2;1,1"]
        for token in raw_token_list:
            if ";" in token:
                """
                处理条件判断语句 "[True]2;1,1"
                目的：将条件和两种做法分别置入三个列表中
                """
                do_when_true = token[token.find("]") + 1:token.find(";")] # 分离True时操作 "2"
                do_when_false = token[token.find(";") + 1:]# 分离False时操作 "1,1"
                condition = [token[token.find("[") + 1:token.find("]")]] # 分离条件 "True"

                if "," in do_when_true or "," in do_when_false:        #"[True]2;1,1"
                    """
                    处理某一分支不止一个操作的情形
                    """
                    do_when_true_list = do_when_true.split(",")
                    do_when_false_list = do_when_false.split(",")
                    # 用"p"补齐两个分支的长度
                    max_len=max(len(do_when_true_list),len(do_when_false_list))
                    do_when_true_list   += ["p"] * (max_len-len(do_when_true_list))
                    do_when_false_list  += ["p"] * (max_len-len(do_when_false_list))
                    # 打进“同上”标记 感谢Csugu的算法
                    for i in range(len(do_when_true_list)-1):
                        condition.append("Same as yesterday")
                    # 推入三大列表
                    self.to_do_list_normal.extend(do_when_true_list)
                    self.to_do_list_special.extend(do_when_false_list)
                    self.condition_list.extend(condition)
                else:
                    """
                    两个分支仅一操作的情形
                    """
                    self.to_do_list_normal.append(do_when_true)
                    self.to_do_list_special.append(do_when_false)
                    self.condition_list.extend(condition)
            else:
                """
                此token不是条件语句
                """
                self.to_do_list_normal.append(token)
                self.to_do_list_special.append("2")
                self.condition_list.append("True")
        assert len(self.to_do_list_normal)==len(self.to_do_list_special)==len(self.condition_list),\
            "[IFAWL开发者断言错误]Autopilot三大列表长度必须相同-若你看到此行句子，请立即联系开发者"
        
    def test(self):
        print(self.to_do_list_normal)
        print(self.condition_list)
        print(self.to_do_list_special)
        print(self.memory)

    def react(self, field_state):

        ps=field_state[0]
        pm=field_state[1]
        cs=field_state[2]
        cm=field_state[3]
        f=field_state[4]
        q=field_state[5]
        w=field_state[6]
        e=field_state[7]


        output=""

        while output in ["","(",")","p"] and self.to_do_list_normal != []:
            try:
                if eval(self.condition_list[0]):
                    try:
                        if self.condition_list[1] == "Same as yesterday":
                            self.condition_list[1]= "True"
                    except IndexError:
                        pass
                    output=self.to_do_list_normal[0]
                else:
                    try:
                        if self.condition_list[1] == "Same as yesterday":
                            self.condition_list[1]= "False"
                    except IndexError:
                        pass
                    output=self.to_do_list_special[0]
            except SyntaxError:
                self.refresh()
                print_plus("自动驾驶读取异常，控制权即将转交给指挥官")
                return input_plus("请输入你的操作|此处不支持自动驾驶")
            if output == "(":
                self.memory=[self.to_do_list_normal, self.to_do_list_special, self.condition_list]
            
            if output == ")":
                self.to_do_list_normal,self.to_do_list_special,self.condition_list=self.memory

            self.condition_list = self.condition_list[1:]
            self.to_do_list_normal = self.to_do_list_normal[1:]
            self.to_do_list_special = self.to_do_list_special[1:]

        return output

    def refresh(self):
        self.condition_list=[]
        self.to_do_list_normal=[]
        self.to_do_list_special=[]
        self.memory=[]

    def get_operation(self, n):
        if self.to_do_list_normal:
            print("自动驾驶接管中<<<")
            return self.react(n)

        operation_input = input_plus("请输入你的操作>>>")
        if "-" in operation_input:
            self.read(operation_input)
            print_plus("自动驾驶数据已录入，准备接管舰船<<<")
            return self.react(n)

        return operation_input

auto_pilot=Auto_pilot_manager()