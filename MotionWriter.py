from enum import Enum
from functools import partial
from time import localtime, strftime, time
from tkinter import BOTH, BOTTOM, END, HORIZONTAL, LEFT, RIGHT, S, SOLID, TOP, W, X, Y, Canvas, Entry, Frame, Label, Menu, PhotoImage, Scrollbar, StringVar, Tk, Button, Toplevel, Scale
from tkinter.filedialog import askopenfilename
from tkinter.font import BOLD, ITALIC, Font
from tkinter.ttk import Combobox, OptionMenu
import tkinter.messagebox as msgbox
from types import FunctionType
from typing import Any, Dict, List, Literal, Tuple
from uuid import uuid4
from os.path import dirname, realpath
from hashlib import sha256
import sys
from traceback import format_tb
folder = dirname(realpath(__file__)) + "\\"
del dirname, realpath
argv = sys.argv

if not "--onHandler" in argv:
    from subprocess import call
    try: call(folder+"Handler.exe")
    except: call("python "+folder+"Handler.py")
    exit()

window = Tk()
window.withdraw()
fake_focus_in = window.focus
AllUUID:List[str] = []
DataDict:Dict[str, Any] = {}
UIDict:Dict[str, Any] = {}
GlobalData:Dict[str, Any] = {
    "img.error":PhotoImage(file=folder+"res\\error.png"),
    "img.x":PhotoImage(file=folder+"res\\x.png"),

    "font.noto.ui":Font(family=folder+"res\\font\\NotoSansKR-Medium.otf", size=10),
    "font.noto.text14":Font(family=folder+"res\\font\\NotoSansKR-Medium.otf", size=14, weight=BOLD),
    "font.kalam.italic":Font(family=folder+"res\\font\\Kalam.ttf", size=10, slant=ITALIC),

    "license.MotionWriter":(folder+"res\\license\\MotionWriter.txt", "8486a10c4393cee1c25392769ddd3b2d6c242d6ec7928e1414efff7dfb2f07ef"),
    "license.Google Open Font":(folder+"res\\license\\Google Open Font.txt", "02d198273c4badb4046f253170297fb3eb3b38dd6c7b445c3c4a53f21bee360e")
}
window.option_add("*Font", GlobalData["font.noto.ui"])
def logger(_type: Literal["INFO", "WARN", "ERROR"], _string: str, _code: str, _source: str = "Log"):
    text = "[" + strftime('%H:%M:%S', localtime(time())) + "] ["+_type+"] [" + _source + " :: " + _code +"] " + {True:"\n", False:""}[len(_string.split("\n")) != 1] + _string
    print(text)
    msg_dict = {"ERROR":msgbox.showerror, "WARN":msgbox.showwarning, "INFO":msgbox.showinfo}
    msg_dict[_type]("MotionWriter", _source + "\n" + _string + "\n" + "CODE: " + _code)
    if _type == "ERROR": exit()
def exc_hook(exctype: type, value, traceback):
    text = "Traceback (most recent call last):\n" + " ".join(format_tb(traceback)) + exctype.__name__
    if len(str(value)): text += ": " + str(value)
    logger("ERROR", text, "ERROR_INTERNAL_PYTHON", "InternalError :: PythonError :: " + str(exctype.__name__))
sys.excepthook = exc_hook
del sys

def GetHash(data:str)->str: return sha256(data.encode()).hexdigest()
for key in filter(lambda key: key.startswith("license."), GlobalData.keys()):
    with open(GlobalData[key][0], "r", encoding="utf-8") as f: text = f.read(); hash_256 = GetHash(text)
    if hash_256 == GlobalData[key][1]: GlobalData[key] = text
    else: logger("ERROR", "License data file about " + key.replace("license.", "") + " is modified.", "ERROR_LICENSE_MODIFIED", "DataError :: LicenseError")
del text, hash_256
class ScrollableFrame(Frame):
    def __init__(self, container, *args, **kwargs):
        self.__frame_master = Frame(container, *args, **kwargs)
        self.__canvas = Canvas(self.__frame_master, bg="#FFFFFF")
        self.__scroll = Scrollbar(self.__frame_master, orient="vertical", command=self.__canvas.yview)
        super().__init__(self.__canvas, bg="#FFFFFF")

        def config_event(e):
            self.__canvas.configure(
                height=self.cget("height"),
                scrollregion=self.__canvas.bbox("all")
            )
        self.bind("<Configure>", config_event)
        
        self.__canvas.place(x=0, y=-2, relwidth=1, relheight=1)
        self.__scroll.pack(side="right", fill="y")
        self.__canvas.create_window((0,0), window=self, anchor="nw", width=float(self.__canvas.cget("width"))*1.5)
        self.__canvas.configure(yscrollcommand=self.__scroll.set)

        self.pack, self.grid, self.place = self.__frame_master.pack, self.__frame_master.grid, self.__frame_master.place
    def update_ui(self): self.__canvas.configure(height=self.cget("height"))


def GetUUID(ignore:List[str]=AllUUID):
    uid = str(uuid4())
    while uid in ignore: uid = str(uuid4())
    AllUUID.append(uid)
    return uid

class FrameWork():
    def __init__(self) -> None: ...
class InputType(Enum):
    Integer = 1
    Float = 2
    String = 3
    Boolean = 4
    File = 5
    Selection = 6
class MotionMeta():
    def __init__(self, loc: str, inputs: Tuple[Tuple[str, InputType, Tuple[Any, ...]], ...]=(("apple", InputType.Selection, "kr", "en"), ("fruit", InputType.Selection, "appele", "banana", "kiwi"), ("img", InputType.File, None))) -> None:
        self.loc = loc
        self.inputs = inputs
        self.__ui_data__:Dict[str, List[Any]] = {}
        self.getFunc:Dict[str,FunctionType] = {}
        self.getInput:Dict[str,Any] = {}
    def __reset_data__(self):
        for name, func in self.getFunc.items():
            self.getInput[name] = func()
    @property
    def data(self):
        self.__reset_data__()
        return self.getInput
    def draw(self, __MotionUI):
        frame = Frame(__MotionUI.frame_repos)
        frame.pack(side=TOP, fill=BOTH)
        line = 1
        for name, input_type, *input_args in self.inputs:
            Label(frame, text=name+":").grid(row=line, column=1, sticky=W)
            if input_type == InputType.Integer:
                #TODO
                ...
            elif input_type == InputType.Float:
                #TODO
                ...
            elif input_type == InputType.String:
                entry = Entry(frame)
                entry.grid(row=line, column=2, sticky=W)
                self.getFunc[name] = entry.get
            elif input_type == InputType.Boolean:
                var = StringVar()
                OptionMenu(frame, var, "true", *("true", "false")).grid(row=line, column=2, sticky=W)
                self.getFunc[name] = var.get
            elif input_type == InputType.File:
                self.__ui_data__[name] = [Label(frame, text="C:/", font="TkDefaultFont")]
                self.__ui_data__[name][0].grid(row=line, column=2, sticky=W)
                def loadName(name:str):
                    self.__ui_data__[name][0].config(text=askopenfilename(filetypes=(("All Files", "*.*"),)))
                    self.__ui_data__[name][0].update()
                Button(frame, text="...", command=partial(loadName, name)).grid(row=line, column=3, sticky=W)
                self.getFunc[name] = lambda: self.__ui_data__[name][0].cget("text")
            elif input_type == InputType.Selection:
                var = StringVar()
                OptionMenu(frame, var, input_args[0], *input_args).grid(row=line, column=2, sticky=W)
                self.getFunc[name] = var.get
            line += 1
class MotionData():
    def __init__(self, sprite, meta: MotionMeta):
        self.uuid = GetUUID()
        self.sprite = sprite
        self.meta = meta

        DataDict[self.uuid] = self
        UIDict[self.uuid] = MotionUI(self.uuid)
        self.sprite.add_motion(self)
    @property
    def UI(self): return UIDict[self.uuid]
    def remove(self):
        self.sprite.remove_motion(self)
        del DataDict[self.uuid]
        del UIDict[self.uuid]

class MotionUI():
    def __init__(self, uuid:str) -> None:
        self.uuid = uuid
        self.start_tick = 0
        self.end_tick = self.data.sprite.scene.length
    @property
    def data(self)->MotionData: return DataDict[self.uuid]
    def draw(self):
        self.frame = Frame(self.data.sprite.UI.frame_sprite_edit_motion, bg="#FFFFFF")
        self.frame.pack(fill=X, padx=5, pady=10)
        self.frame_repos = Frame(self.frame)
        self.frame_repos.pack(side=LEFT)
        self.frame_up = Frame(self.frame_repos)
        self.frame_up.pack(fill="x")
        self.label_meta_loc = Label(self.frame_up, text=self.data.meta.loc, font=GlobalData["font.kalam.italic"])
        self.label_meta_loc.pack(side="left")
        self.btn_delete = Button(self.frame_up, text="X", command=self.remove)
        self.btn_delete.pack(side="right")

        self.data.meta.draw(self)
    def remove(self):
        self.data.remove()
        for obj in self.__dict__:
            try: self.__getattribute__(obj).destroy()
            except: pass

class SpriteData():
    def __init__(self, scene, name:str) -> None:
        self.uuid = GetUUID()
        self.scene = scene
        self.init_name = name
        self.motions:List[MotionData] = []

        DataDict[self.uuid] = self
        UIDict[self.uuid] = SpriteUI(self.uuid)
        self.scene.add_sprite(self)
        MotionData(self, MotionMeta("defualt.graphic.ImageLoader"))
        MotionData(self, MotionMeta("defualt.graphic.ImageLoader"))
        MotionData(self, MotionMeta("defualt.graphic.ImageLoader"))
        MotionData(self, MotionMeta("defualt.graphic.ImageLoader"))
        MotionData(self, MotionMeta("defualt.graphic.ImageLoader"))
        MotionData(self, MotionMeta("defualt.graphic.ImageLoader"))
        MotionData(self, MotionMeta("defualt.graphic.ImageLoader"))
        MotionData(self, MotionMeta("defualt.graphic.ImageLoader"))
    def draw(self):
        self.UI.draw()
    def add_motion(self, motion:MotionData):
        self.motions.append(motion)
        motion.UI.draw()
    @property
    def UI(self): return UIDict[self.uuid]
    def remove_motion(self, motion: MotionData):
        self.motions.remove(motion)
    def remove(self):
        if len(self.scene.sprites) == 1: return False
        self.scene.remove_sprite(self)
        del DataDict[self.uuid]
        del UIDict[self.uuid]
        return True
class SpriteUI():
    def __init__(self, uuid:str) -> None:
        self.uuid = uuid

        self.frame_sprite_list = Frame(self.data.scene.UI.frame_sprite_list, bg="#FFFFFF")
        self.frame_sprite_list.pack(fill=X)
        self.frame_sprite_list_up = Frame(self.frame_sprite_list, bg="#FFFFFF", cursor="hand2")
        self.frame_sprite_list_up.pack(fill=X, side=TOP)
        self.frame_sprite_list_up.bind("<Button-1>", lambda o: self.focus())
        self.entry_sprite_name_list = Entry(self.frame_sprite_list_up)
        self.entry_sprite_name_list.insert(END, self.data.init_name)
        self.entry_sprite_name_list.pack(side=LEFT)
        self.entry_sprite_name_list.bind("<Return>", lambda o: self.focus())
        self.btn_sprite_remove = Button(self.frame_sprite_list_up, image=GlobalData["img.x"], bg="#FFFFFF", relief=SOLID, bd=0, command=self.remove)
        self.btn_sprite_remove.pack(side=RIGHT, padx=40)

        self.frame_sprite_list_down = Frame(self.frame_sprite_list, bg="#F0F0F0")
        self.label_sprite_pos_x = Label(self.frame_sprite_list_down, text="X:", bg="#F0F0F0")
        self.label_sprite_pos_x.pack(side=LEFT)
    def remove(self):
        isok = self.data.remove()
        if not isok: logger("WARN", "Scene must have at least 1 sprite", "WARN_SPRITE_REMOVE", "InteractionWarn :: SpriteWarn"); return
        for obj in self.__dict__:
            try: self.__getattribute__(obj).destroy()
            except: pass
    @property
    def data(self)->SpriteData: return DataDict[self.uuid]
    @property
    def name(self)->str: return self.entry_sprite_name_list.get()
    def draw(self):
        self.frame_sprite_edit = Frame(self.data.scene.UI.frame_split_right, bg="#FFFFFF")
        
        self.label_sprite_info = Label(self.frame_sprite_edit, text="", bg="#FFFFFF", justify=LEFT, anchor=W)
        self.label_sprite_info.pack(fill=X, pady=10)

        self.frame_sprite_edit_motion = ScrollableFrame(self.frame_sprite_edit, bg="#FFFFFF")
        self.frame_sprite_edit_motion.pack(fill=BOTH, expand=True)
    def focus(self):
        fake_focus_in()
        self.label_sprite_info.config(text="The motions of sprite \""+self.name+"\"")

        [sprite.UI.unfocus() for sprite in self.data.scene.sprites]
        self.frame_sprite_edit.place(x=0, y=0, relwidth=1, relheight=1)
        self.frame_sprite_list_down.pack(fill=X, side=TOP)
    def unfocus(self):
        self.frame_sprite_edit.place_forget()
        self.frame_sprite_list_down.pack_forget()
    def add_motion(self):
        ...
        #TODO
    def remove_motion(self):
        ...
        #TODO

class SceneData():
    def __init__(self, project, name:str, length:int) -> None:
        self.project = project
        self.name = name
        self.length = length
        self.uuid = GetUUID()

        self.sprites:List[SpriteData] = []

        DataDict[self.uuid] = self

        UIDict[self.uuid] = SceneUI(self.uuid)
        self.project.add_scene(self)
        SpriteData(self, "New Sprite")
    def remove_sprite(self, sd:SpriteData):
        try: self.sprites[self.sprites.index(sd)-1].UI.focus()
        except: self.sprites[self.sprites.index(sd)+1].UI.focus()
        self.sprites.remove(sd)
    def add_sprite(self, sd: SpriteData):
        self.sprites.append(sd)
        sd.draw()
        sd.UI.focus()
        self.UI.addNewSpriteFrame.pack_forget()
        self.UI.addNewSpriteFrame.pack(fill=X)
    def draw(self):
        #[sprite.draw() for sprite in self.sprites]
        self.UI.draw()
    @property
    def UI(self): return UIDict[self.uuid]
class SceneUI():
    def __init__(self, uuid:str) -> None:
        self.uuid = uuid

        self.btn_scene = Button(self.data.project.UI.sceneBarFrame, text=self.data.name+"\n("+str(self.data.length)+" tick)", width=10, height=40, command=self.focus)
        self.btn_scene.pack(side=LEFT, padx=1)
    @property
    def data(self): return DataDict[self.uuid]
    def draw(self) -> None:
        #self.TEST = Button(UIDict[self.data.project.uuid].workspace)
        #self.TEST.place(x=10, y=10)

        project_ui = UIDict[self.data.project.uuid]
        workspace:Frame = project_ui.workspace

        self.frame = Frame(workspace, bg="#FFFFFF")

        self.frame_split_left = Frame(self.frame)
        self.frame_split_left.place(relx=0, rely=0, relwidth=0.4, relheight=1)

        self.frame_video = Frame(self.frame_split_left, bg="#FFFFFF", bd=1, relief="solid") #flat, groove, raised, ridge, solid, or sunken
        self.frame_video.place(x=0, y=0, relwidth=1, relheight=0.4)
        self.frame_video_error = Frame(self.frame_video, bg="#5a5a5a")
        self.frame_video_error.place(x=0, y=0, relwidth=1, relheight=1)
        self.img_video_error = Label(self.frame_video_error, image=GlobalData["img.error"], bg="#5a5a5a")
        self.img_video_error.place(relx=0.4, rely=0.15, width=100, height=100)
        self.label_video_error1 = Label(self.frame_video_error, text="동영상이 물에 젖어서 말리는 중입니다.. :(", bg="#5a5a5a", fg="#FFFFFF", font=GlobalData["font.noto.text14"])
        self.label_video_error1.place(relx=0.2, rely=0.5)
        self.label_video_error2 = Label(self.frame_video_error, text="잠시만 기다려 주세요!", bg="#5a5a5a", fg="#FFFFFF", font=GlobalData["font.noto.text14"])
        self.label_video_error2.place(relx=0.32, rely=0.6)
        self.frame_video_control = Frame(self.frame_video, bg="#FFFFFF", bd=2, relief="solid")
        self.frame_video_control.pack(side=BOTTOM, fill=X)
        self.btn_video_start = Button(self.frame_video_control, text="▶")
        self.btn_video_start.pack(side=LEFT)
        self.scale_time = Scale(self.frame_video_control, orient=HORIZONTAL, fg="#007AD9", troughcolor="#FFFFFF", bg="#007AD9", showvalue=False, length=300, sliderlength=10, sliderrelief="flat")
        self.scale_time.pack(side=LEFT, fill=Y)
        
        self.frame_sprite_list = ScrollableFrame(self.frame_split_left, bg="#F0F0F0")
        self.frame_sprite_list.place(relx=0, rely=0.4, relwidth=1, relheight=0.588)
        self.addNewSpriteFrame = Frame(self.frame_sprite_list)
        self.addNewSpriteFrame.pack(fill=X)
        self.addNewSpriteBtn = Button(self.addNewSpriteFrame, text="새로운 스프라이트 추가", command=self.add_sprite)
        self.addNewSpriteBtn.pack(side=RIGHT)

        self.frame_split_right = Frame(self.frame, bg="#FFFFFF")
        self.frame_split_right.place(relx=0.4, rely=0, relwidth=0.6, relheight=1)
        #[Label(self.frame_sprite_list, text=str(i)+"번째 스프라이트입니다!").pack() for i in range(100)]

        try: self.data.sprites[0].draw()
        except: pass
    def add_sprite(self, name=""):
        self.tk_sprite_maker = Toplevel(window)
        self.tk_sprite_maker.deiconify()
        self.tk_sprite_maker.title("")
        self.tk_sprite_maker.geometry("190x65")
        self.label_sprite_maker_name = Label(self.tk_sprite_maker, text="이름", anchor=S)
        self.entry_sprite_maker_name = Entry(self.tk_sprite_maker, width=25)
        self.entry_sprite_maker_name.insert(END, name)
        self.entry_sprite_maker_name.focus()
        self.label_sprite_maker_name.pack(fill=X, ipady=2)
        self.entry_sprite_maker_name.pack()
        self.frame_sprite_maker_btn = Frame(self.tk_sprite_maker)
        self.btn_sprite_maker_done = Button(self.frame_sprite_maker_btn, text="Done", command=self.__add_sprite_done)
        self.btn_sprite_maker_exit = Button(self.frame_sprite_maker_btn, text="Exit", command=self.tk_sprite_maker.destroy)
        self.frame_sprite_maker_btn.pack(fill=X, ipady=20)
        self.btn_sprite_maker_done.pack(side=LEFT)
        self.btn_sprite_maker_exit.pack(side=RIGHT)
    def __add_sprite_done(self):
        name = self.entry_sprite_maker_name.get()
        self.tk_sprite_maker.destroy()
        if name.replace(" ", "") == "": msgbox.showwarning("New Scene", "please type text"); return self.add_sprite(name)
        SpriteData(self.data, name)
    def focus(self): 
        [scene.UI.unfocus() for scene in self.data.project.scenes]
        self.frame.place(x=10, y=10, relwidth=0.985, relheight=1)#width=workspace.place_info()["width"], height=workspace.place_info()["height"])
    def unfocus(self):
        self.frame.place_forget()

class ProjectData():
    def __init__(self, name:str="untitled") -> None:
        self.name = name
        self.uuid = GetUUID()
        DataDict[self.uuid] = self

        self.scenes:List[SceneData] = []

        
        global UIDict
        UIDict = {self.uuid:ProjectUI(self.uuid)}
    def draw(self):
        #[scene.draw() for scene in self.scenes]
        UIDict[self.uuid].draw()
    def add_scene(self, scene: SceneData):
        self.scenes.append(scene)
        scene.draw()
        scene.UI.focus()
        self.UI.addNewSceneBtn.pack_forget()
        self.UI.addNewSceneBtn.pack(side=LEFT, padx=5)
    @property
    def UI(self): return UIDict[self.uuid]
class ProjectUI():
    def __init__(self, uuid:str):
        self.uuid = uuid


        #Make Tk Window
        self.x, self.y = 1400, 750
        window.title(self.data.name)
        window.geometry(str(self.x)+"x"+str(self.y))
        window.resizable(0, 0)

        self.screen = Frame(window, bg="#FFFFFF")
        self.screen.place(x=0, y=0, relwidth=1, relheight=1)

        self.sceneBarFrame = Frame(self.screen, bg="#FFFFFF")
        self.sceneBarFrame.place(x=40, y=10, relwidth=1, height=40)

        self.addNewSceneBtn = Button(self.sceneBarFrame, text="+", bg="#8080FF", fg="#FFFFFF", width=2, command=self.add_scene)

        self.workspace = Frame(self.screen, bg="#FFFFFF")
        self.workspace.place(x=0, y=50, relwidth=1, height=self.y-60)

        menubar=Menu(window)

        file_help=Menu(menubar, tearoff=0)
        file_help.add_command(label = "새로 만들기")
        file_help.add_command(label = "불러오기")
        file_help.add_command(label = "저장하기")
        file_help.add_command(label = "다른 이름으로 저장하기", command=self.save_as_new_name)
        file_help.add_separator()
        file_help.add_command(label = "내보내기")
        menubar.add_cascade(label="파일", menu=file_help)

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
    def save_as_new_name(self):
        __file = askopenfilename#TODO
    def open_win_license(self, __type):
        self.win_license.deiconify()
        self.win_license.title("MotionWriter :: License :: " + __type.replace("license.", ""))
        try: self.label_license.destroy()
        except: ...
        self.label_license = Label(self.frame_license, text=GlobalData[__type], justify=LEFT)
        self.label_license.pack(fill=BOTH)
        self.frame_license.update_ui()
    def add_scene(self, name="", tick="100", combo="tick(s)"):
        self.tk_scene_maker = Toplevel(window)
        self.tk_scene_maker.title("")
        self.tk_scene_maker.geometry("190x105")
        self.label_scene_maker_name = Label(self.tk_scene_maker, text="이름", anchor=S)
        self.entry_scene_maker_name = Entry(self.tk_scene_maker, width=25)
        self.entry_scene_maker_name.insert(END, name)
        self.label_scene_maker_name.pack(fill=X, ipady=2)
        self.entry_scene_maker_name.pack()
        self.entry_scene_maker_name.focus()
        self.label_scene_maker_tick = Label(self.tk_scene_maker, text="길이", anchor=S)
        self.frame_scene_maker_tick = Frame(self.tk_scene_maker)
        self.combo_scene_maker_tick = Combobox(self.frame_scene_maker_tick, values=("tick(s)", "second(s)"), width=8)
        self.combo_scene_maker_tick.set(combo)
        self.entry_scene_maker_tick = Entry(self.frame_scene_maker_tick, width=14)
        self.entry_scene_maker_tick.insert(END, tick)
        self.label_scene_maker_tick.pack(fill=X, ipady=2)
        self.frame_scene_maker_tick.pack()
        self.combo_scene_maker_tick.pack(side=RIGHT)
        self.entry_scene_maker_tick.pack(side=LEFT)
        self.frame_scene_maker_btn = Frame(self.tk_scene_maker)
        self.btn_scene_maker_done = Button(self.frame_scene_maker_btn, text="Done", command=self.__add_scene_done)
        self.btn_scene_maker_exit = Button(self.frame_scene_maker_btn, text="Exit", command=self.tk_scene_maker.destroy)
        self.frame_scene_maker_btn.pack(fill=X, ipady=20)
        self.btn_scene_maker_done.pack(side=LEFT)
        self.btn_scene_maker_exit.pack(side=RIGHT)
    def __add_scene_done(self):
        name, tick, combo = self.entry_scene_maker_name.get(), self.entry_scene_maker_tick.get(), self.combo_scene_maker_tick.get()
        self.tk_scene_maker.destroy()
        if len(name) > 10: logger("WARN", "name is too long\nname must be shorter or same 10 letters", "WARN_LENGTH_LIMIT", "ObjectHandleWarn :: SceneWarn"); return self.add_scene(name)
        if "" in (name.replace(" ", ""), tick): logger("WARN", "you must fill all text box", "WARN_INPUT_EMPTY"); return self.add_scene(name, tick, combo)
        try: tick = int(tick)
        except: msgbox.showwarning("New Scene", tick+" isn't a number"); return self.add_scene(name, tick, combo)
        if combo == "second(s)": tick *= 20 
        SceneData(self.data, name, tick)
    @property
    def data(self): return DataDict[self.uuid]
    def draw(self):
        #[btn.pack_forget() for btn in self.sceneButton]
        #del self.sceneButton
        #[UIDict[scene.uuid].draw() for scene in self.data.scenes]
        self.data.scenes[0].UI.focus()
        GlobalData["sys.winRunning"] = True
        window.deiconify()
        window.mainloop()
pro = ProjectData()
pd1 = SceneData(pro, "asdf1", 10)
pd2 = SceneData(pro, "asdf2", 50)
pd3 = SceneData(pro, "asdf3", 5)
pro.draw()