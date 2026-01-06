from core.Module1_txt import print_plus,input_plus
from core.Module2_json_loader import json_loader

ALL_POLT_DATA:dict[str,dict[str,dict[str,str]]] = json_loader.load("plots")

class Plot:

    def __init__(self,session,paragraph):
        self.title = ALL_POLT_DATA[session][paragraph]["title"]
        self.raw_txt = ALL_POLT_DATA[session][paragraph]["raw_txt"]
        self.lines = self.raw_txt.split("\n\n")

    @staticmethod
    def __processed(line:str):
        out = line
        if line.startswith("-"):
            out = "[" + line[1:]
            out = out.replace("-","]")
            return out
        if line.startswith("【") and line.endswith("】"):
            content = line[1:-1]
            out = "[enter]" + content
            return out
        return out

    def play(self,info_map):
        for line in self.lines:
            processed = self.__processed(line)
            processed = processed.format_map(info_map)
            if processed.startswith("[enter]"):
                input_plus(processed)
                print()
            else:
                print_plus(processed)
                print()

class PlotManager:
    def __init__(self):
        self.plots:dict[int,dict[int,Plot]] = {}
        for session in ALL_POLT_DATA:
            self.plots[int(session)] = {}
            for paragraph in ALL_POLT_DATA[session]:
                self.plots[int(session)][int(paragraph)] = Plot(session,paragraph)

        self.information_map = {}

    def set_information_map(self,info_map:dict):
        self.information_map = info_map

    def play_plot(self,session:int,paragraph:int):
        self.plots[session][paragraph].play(self.information_map)

plot_manager = PlotManager()