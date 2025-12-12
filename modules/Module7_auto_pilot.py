class Auto_pilot_manager:#自动驾驶

    def __init__(self):
        self.to_do_list=[]
        self.to_do_list_spc=[]
        self.if_list=[]
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
        self.to_do_list=[]
        self.to_do_list_spc=[]
        self.if_list=[]
        # 按照减号分割token
        raw_token_list = txt.split("-")     #["2","2","[True]2;1,1"]
        for token in raw_token_list:
            if ";" in token:          #"[True]2;1,1"
                pre_to_do=token[token.find("]")+1:token.find(";")]#"2"
                pre_to_do_spc=token[token.find(";")+1:]#"1,1"
                pre_if = [token[token.find("[") + 1:token.find("]")]]

                if "," in pre_to_do or "," in pre_to_do_spc:        #"[True]2;1,1"

                    pre_to_do=pre_to_do.split(",")
                    pre_to_do_spc=pre_to_do_spc.split(",")
                    
                    max_len=max(len(pre_to_do),len(pre_to_do_spc))
                    pre_to_do+=["p"]*(max_len-len(pre_to_do))
                    pre_to_do_spc+=["p"]*(max_len-len(pre_to_do_spc))

                    for i in range(len(pre_to_do)-1):
                        pre_if.append("z")
                    for i in range(len(pre_to_do)):
                        self.to_do_list.append(pre_to_do[i])
                        self.to_do_list_spc.append(pre_to_do_spc[i])
                        self.if_list.append(pre_if[i])
                else:
                    self.to_do_list.append(token[token.find("]")+1:token.find(";")])
                    self.to_do_list_spc.append(token[token.find(";")+1:])
                    self.if_list.append(token[token.find("[")+1:token.find("]")])
            else:
                self.to_do_list.append(token)
                self.to_do_list_spc.append("2")
                self.if_list.append("True")
        
    def test(self):
        print(self.to_do_list)
        print(self.if_list)
        print(self.to_do_list_spc)
        print(self.memory)

    def react(self, field_state):

        PS=field_state[0]
        PM=field_state[1]
        CS=field_state[2]
        CM=field_state[3]
        F=field_state[4]


        output=""

        while output in ["","(",")","p"] and self.to_do_list != []:
            if eval(self.if_list[0]):
                try:
                    if self.if_list[1] == "z":
                        self.if_list[1]="True"
                except:
                    pass
                output=self.to_do_list[0]
            else:
                try:
                    if self.if_list[1] == "z":
                        self.if_list[1]="False"
                except:
                    pass
                output=self.to_do_list_spc[0]

            if output == "(":
                self.memory=[self.to_do_list,self.to_do_list_spc,self.if_list]
            
            if output == ")":
                self.to_do_list,self.to_do_list_spc,self.if_list=self.memory

            try:
                self.if_list=self.if_list[1:]
                self.to_do_list=self.to_do_list[1:]
                self.to_do_list_spc=self.to_do_list_spc[1:]
            except:
                self.if_list=[]
                self.to_do_list=[]
                self.to_do_list_spc=[]
        return output

    def refresh(self):
        self.if_list=[]
        self.to_do_list=[]
        self.to_do_list_spc=[] 
        self.memory=[]      

    def get(self,n):
        if not self.to_do_list:
            i=input(">>>")
            if "-"in i:
                self.read(i)
                print("已录入，准备接管")
                i = self.react(n)
        else:
            print("自动驾驶进行中")
            i = self.react(n)
        return i

auto_pilot=Auto_pilot_manager()