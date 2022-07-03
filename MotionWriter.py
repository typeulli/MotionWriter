from functools import partial
from time import localtime, strftime, time
from tkinter import BOTH, BOTTOM, HORIZONTAL, LEFT, NW, X, Y, Canvas, Frame, Label, LabelFrame, Menu, PhotoImage, Scrollbar, Tk, Button, Toplevel, Scale
from tkinter.font import BOLD, Font
from tkinter.ttk import Notebook
import tkinter.messagebox as msgbox
from typing import Any, Dict, List, Literal, Union
from uuid import uuid4
from os.path import dirname, realpath
from hashlib import sha256
#from numba.experimental import jitclass

folder = dirname(realpath(__file__)) + "\\"

AllUUID:List[str] = []
DataDict:Dict[str, Any] = {}
UIDict:Dict[str, Any] = {}
GlobalData:Dict[str, Any] = {
    "img.error":None,

    "font.noto.ui":folder+"res\\NotoSansKR-Medium.otf",
    "font.noto.text":folder+"res\\NotoSansKR-Medium.otf",

    "license.MotionWriter":(folder+"res\\license\\MotionWriter.txt", "21c92ee89975a5972f20eb1e1aa9882ec0aead02fc8995c6607657b4d8d6354b"),
    "license.Google Open Font":(folder+"res\\license\\Google Open Font.txt", "02d198273c4badb4046f253170297fb3eb3b38dd6c7b445c3c4a53f21bee360e")
}

window = Tk()
window.withdraw()

def logger(_type: Literal["INFO", "WARN", "ERROR"], _string: str, _code: str, _source: str = "Log"):
    text = "[" + strftime('%H:%M:%S', localtime(time())) + "] ["+_type+"] [" + _source + " :: " + _code +"] " + _string
    print(text)
    if _type == "ERROR":
        msgbox.showerror("MotionWriter", _source + "\n" + _string + "\n" + "CODE: " + _code)
        exit()

for key in filter(lambda key: key.startswith("license."), GlobalData.keys()):
    with open(GlobalData[key][0], "r", encoding="utf-8") as f: text = f.read(); hash_256 = sha256(text.encode("utf-8")).hexdigest()
    if hash_256 == GlobalData[key][1]: GlobalData[key] = text
    else: logger("ERROR", "License data file about " + key.replace("license.", "") + " is modified.", "ERR_LICENSE_MODIFIED", "DataError :: LicenseError")
del text, hash_256

class ScrollableFrame(Frame):
    def __init__(self, container, *args, **kwargs):
        self.__frame_master = Frame(container, *args, **kwargs)
        self.__canvas = Canvas(self.__frame_master)
        self.__scroll = Scrollbar(self.__frame_master, orient="vertical", command=self.__canvas.yview)
        super().__init__(self.__canvas)

        self.bind(
            "<Configure>",
            lambda e: self.__canvas.configure(
                scrollregion=self.__canvas.bbox("all")
        ))
        
        self.__canvas.create_window((0,0), window=self, anchor="nw")
        self.__canvas.configure(yscrollcommand=self.__scroll.set)
        
        self.__canvas.place(x=0, y=0, relwidth=1, relheight=1)
        self.__scroll.pack(side="right", fill="y")

        self.pack, self.grid, self.place = self.__frame_master.pack, self.__frame_master.grid, self.__frame_master.place


def GetUUID(ignore:List[str]=AllUUID):
    uid = str(uuid4())
    while uid in ignore: uid = str(uuid4())
    AllUUID.append(uid)
    return uid

class FrameWork():
    def __init__(self) -> None: ...

class Motion():
    def __init__(self) -> None: ...

class SpriteData():
    def __init__(self, name:str) -> None:
        self.uuid = GetUUID()
        DataDict[self.uuid] = self
    def show(self):
        UIDict[self.uuid] = SpriteUI(self.uuid)
    @property
    def UI(self): return UIDict[self.uuid]
class SpriteUI():
    def __init__(self, uuid:str) -> None:
        self.uuid = uuid
    @property
    def data(self): return DataDict[self.uuid]

class PageData():
    def __init__(self, project, name:str, length:int) -> None:
        self.project = project
        self.name = name
        self.length = length
        self.uuid = GetUUID()

        self.sprites:List[SpriteData] = []

        DataDict[self.uuid] = self

        self.project.add_page(self)
    def show(self):
        [sprite.show() for sprite in self.sprites]
        UIDict[self.uuid] = PageUI(self.uuid)
    @property
    def UI(self): return UIDict[self.uuid]
class PageUI():
    def __init__(self, uuid:str) -> None:
        self.uuid = uuid
    @property
    def data(self): return DataDict[self.uuid]
    def show(self) -> None:
        #self.TEST = Button(UIDict[self.data.project.uuid].workspace)
        #self.TEST.place(x=10, y=10)

        project_ui = UIDict[self.data.project.uuid]
        workspace:Frame = project_ui.workspace

        self.btn_page = Button(project_ui.pageBarFrame, text=self.data.name+"\n("+str(self.data.length)+" tick)", width=10, height=40)
        self.btn_page.pack(side=LEFT)

        self.frame = Frame(workspace, bg="#FFFFFF")
        self.frame.place(x=0, y=0, relwidth=1, relheight=1)#width=workspace.place_info()["width"], height=workspace.place_info()["height"])

        self.frame_split_left = Frame(self.frame)
        self.frame_split_left.place(x=10, y=10, relwidth=0.4, relheight=1)

        self.frame_video = Frame(self.frame_split_left, bg="#FFFFFF", bd=1, relief="solid") #flat, groove, raised, ridge, solid, or sunken
        self.frame_video.place(x=0, y=0, relwidth=1, relheight=0.4)
        self.frame_video_error = Frame(self.frame_video, bg="#5a5a5a")
        self.frame_video_error.place(x=0, y=0, relwidth=1, relheight=1)
        self.img_video_error = Label(self.frame_video_error, image=GlobalData["img.error"], bg="#5a5a5a")
        self.img_video_error.place(relx=0.4, rely=0.15, width=100, height=100)
        self.label_video_error1 = Label(self.frame_video_error, text="동영상이 물에 젖어서 말리는 중입니다.. :(", bg="#5a5a5a", fg="#FFFFFF", font=GlobalData["font.noto.text"])
        self.label_video_error1.place(relx=0.2, rely=0.5)
        self.label_video_error2 = Label(self.frame_video_error, text="잠시만 기다려 주세요!", bg="#5a5a5a", fg="#FFFFFF", font=GlobalData["font.noto.text"])
        self.label_video_error2.place(relx=0.32, rely=0.6)
        self.frame_video_control = Frame(self.frame_video, bg="#FFFFFF", bd=2, relief="solid")
        self.frame_video_control.pack(side=BOTTOM, fill=X)
        self.btn_video_start = Button(self.frame_video_control, text="▶")
        self.btn_video_start.pack(side=LEFT)
        self.scale_time = Scale(self.frame_video_control, orient=HORIZONTAL, fg="#007AD9", troughcolor="#FFFFFF", bg="#007AD9", showvalue=False, length=300, sliderlength=10, sliderrelief="flat")
        self.scale_time.pack(side=LEFT, fill=Y)

        self.frame_sprite_list = ScrollableFrame(self.frame_split_left, bg="#F0F0F0")
        self.frame_sprite_list.place(relx=0, rely=0.4, relwidth=1, relheight=0.588)
        [Label(self.frame_sprite_list, text=str(i)+"번째 스프라이트입니다!").pack() for i in range(100)]

class ProjectData():
    def __init__(self, name:str="untitled") -> None:
        self.name = name
        self.uuid = GetUUID()
        DataDict[self.uuid] = self

        self.pages:List[PageData] = []
    def show(self):
        global UIDict
        UIDict = {self.uuid:ProjectUI(self.uuid)}
        [page.show() for page in self.pages]
        UIDict[self.uuid].show()
    def add_page(self, page: PageData):
        self.pages.append(page)
    @property
    def UI(self): return UIDict[self.uuid]
class ProjectUI():
    def __init__(self, uuid:str):
        self.uuid = uuid


        #Make Tk Window
        self.x, self.y = 1400, 800
        window.title(self.data.name)
        window.geometry(str(self.x)+"x"+str(self.y))
        window.resizable(0, 0)

        self.screen = Frame(window, bg="#FFFFFF")
        self.screen.place(x=0, y=0, relwidth=1, relheight=1)

        self.pageBarFrame = Frame(self.screen, bg="#FFFFFF")
        self.pageBarFrame.place(x=40, y=10, relwidth=1, height=40)

        self.workspace = Frame(self.screen, bg="#FFFFFF")
        self.workspace.place(x=0, y=50, relwidth=1, height=self.y-60)

        GlobalData["img.error"] = PhotoImage(file=folder+"res\\error.png")
        GlobalData["font.noto.ui"] = Font(family=GlobalData["font.noto.ui"], size=10)
        GlobalData["font.noto.text"] = Font(family=GlobalData["font.noto.text"], size=14, weight=BOLD)
        window.option_add("*Font", GlobalData["font.noto.ui"])

        menubar=Menu(window)

        menu_help=Menu(menubar, tearoff=0)
        menu_help.add_command(label = "도움말")
        menu_help.add_separator()
        menu_help.add_command(label="라이선스", state="disabled")
        for key in filter(lambda key: key.startswith("license."), GlobalData.keys()):
            menu_help.add_command(label=key.replace("license.", ""), command=partial(self.open_win_license, key))
        menubar.add_cascade(label="도움말", menu=menu_help)

        window.config(menu=menubar)


        self.win_license = Toplevel(window)
        self.win_license.geometry("600x300")
        self.win_license.withdraw()
        self.win_license.protocol("WM_DELETE_WINDOW", self.win_license.withdraw)
        self.frame_license = ScrollableFrame(self.win_license)
        self.frame_license.place(x=0, y=0, relwidth=1, relheight=1)
    def open_win_license(self, __type):
        self.win_license.deiconify()
        self.win_license.title("MotionWriter :: License :: " + __type.replace("license.", ""))
        try: self.label_license.destroy()
        except: ...
        self.label_license = Label(self.frame_license, text=GlobalData[__type], justify=LEFT)
        self.label_license.pack(fill=BOTH)
    @property
    def data(self): return DataDict[self.uuid]
    def show(self):
        #[btn.pack_forget() for btn in self.pageButton]
        #del self.pageButton
        [UIDict[page.uuid].show() for page in self.data.pages]
        GlobalData["sys.winRunning"] = True
        window.deiconify()
        window.mainloop()
pro = ProjectData()
PageData(pro, "asdf1", 10)
PageData(pro, "asdf2", 50)
PageData(pro, "asdf3", 5)
pro.show()