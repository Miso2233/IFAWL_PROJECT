class Auto_pilot_manager:#自动驾驶

    to_do_list=[]
    to_do_list_spc=[]
    if_list=[]
    memory=[]

    def read(self,txt:str):
        txt=txt.replace("(","(-")
        txt=txt.replace("])","]);p")
        self.to_do_list=[]
        self.to_do_list_spc=[]
        self.if_list=[]
        raw_list=txt.split("-")     #["2","2","[True]2;1,1"]
        for i in range(len(raw_list)):
            raw=raw_list[i]
            if ";" in raw:          #"[True]2;1,1"
                pre_to_do=raw[raw.find("]")+1:raw.find(";")]#"2"
                pre_to_do_spc=raw[raw.find(";")+1:]#"1,1"
                pre_if=[]
                pre_if.append(raw[raw.find("[")+1:raw.find("]")])

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
                    self.to_do_list.append(raw[raw.find("]")+1:raw.find(";")])
                    self.to_do_list_spc.append(raw[raw.find(";")+1:])
                    self.if_list.append(raw[raw.find("[")+1:raw.find("]")])
            else:
                self.to_do_list.append(raw)
                self.to_do_list_spc.append("2")
                self.if_list.append("True")
        
    def test(self):
        print(self.to_do_list)
        print(self.if_list)
        print(self.to_do_list_spc)
        print(self.memory)

    def react(self,n):

        PS=n[0]
        PM=n[1]
        CS=n[2]
        CM=n[3]
        F=n[4]


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
        if self.to_do_list==[]:
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