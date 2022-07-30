from sys import exit
from copy import deepcopy
from enum import Enum
from functools import partial
from json import dump, loads
from math import cos, pi, sin
from os import listdir
from time import localtime, strftime, time
from tkinter import BOTH, BOTTOM, DISABLED, END, HORIZONTAL, LEFT, NORMAL, RIGHT, S, SOLID, TOP, W, X, Y, Canvas, Frame, Label, Menu, PhotoImage, Scrollbar, StringVar, Tk, Button, Toplevel, Scale
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.font import BOLD, ITALIC, Font
from tkinter.ttk import OptionMenu, Entry, Progressbar
import tkinter.messagebox as msgbox
from types import FunctionType
from typing import Any, Dict, List, Literal, Tuple, Union
from uuid import uuid4
from os.path import dirname, realpath, exists
from hashlib import sha256
import sys
from traceback import format_tb
from zipfile import ZipFile, is_zipfile
from thefuzz.process import extract
import cv2
from numpy import zeros, uint8, ndarray
from numba import jit
folder = dirname(realpath(__file__)) + "\\"
del dirname, realpath
argv = sys.argv
def start_sub(*args):
    from subprocess import call
    try: call(folder+"Handler.exe "+" ".join(args) + " > nul")
    except: pass
    try: call("python "+folder+"Handler.py "+" ".join(args) + " > nul")
    except: pass
if (not "--debug" in argv):
    if not "--onHandler" in argv:
        start_sub(*argv[1:])
        exit()
del exists


# prefab functions
def imread(path):
    return cv2.cvtColor(cv2.imread(path), cv2.COLOR_BGR2BGRA)#, cv2.IMREAD_UNCHANGED
@jit
def get_all_dot(img: ndarray) -> ndarray:
    "return all dots in the image"
    dots = zeros((img.shape[0], img.shape[1]), dtype=uint8)
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            if img[i, j, 3] != 0:
                dots[i, j] = 1
    return dots
@jit
def fit_image(img: ndarray) -> ndarray:
    work = 0
    now_len = len(list([d for d in get_all_dot(img[1:-2, 1:-2]) if d != [0,0,0,0]]))
    prev_len = now_len
    while prev_len == now_len:
        work += 1
        img = img[1:-2, 1:-2]
        prev_len = now_len
        now_len = len(list([d for d in get_all_dot(img[1:-2, 1:-2]) if d != [0,0,0,0]]))
    cv2.imshow(img)
    cv2.waitKey(0)
    return img
@jit
def auto_smooth_fill(img: ndarray) -> ndarray:
    "fill all empty point in img with average of connected points"
    distance = 4
    h, w, _ = img.shape
    for y in range(h):
        for x in range(w):
            if list(img[y, x]) == [0, 0, 0, 0]:
                for nx, ny in [(x+dx, y+dy) for dx in range(-distance, distance+1) for dy in range(-distance, distance+1)]:
                    b, g, r, a = [0, 0, 0, 0]
                    count = 0
                    if nx >= 0 and nx < w and ny >= 0 and ny < h:
                        nb, ng, nr, na = img[ny, nx]
                        b += nb; g += ng; r += nr; a += na
                        count += 1
                    if count > 0: img[y, x] = b//count, g//count, r//count, a//count


@jit
def __rotated(pos:Tuple[int, int], center:Tuple[int, int], seta:int)->ndarray:
    seta = seta * pi / 180
    __sin, __cos = sin(seta), cos(seta)
    a, b = center
    x, y = pos
    return (x-a)*__cos - (y-b)*__sin + a, (x-a)*__sin + (y-b)*__cos + b
@jit
def rotate(img:ndarray, center:Tuple[int, int], seta:int)->ndarray:
    "return image of spinned img by seta and pos without using cv2 library"
    h, w, c = img.shape
    seta = seta * pi / 180
    a, b = center
    __cos = cos(seta)
    __sin = sin(seta)
    img_list = []
    max_w, max_h = -999999999, -999999999
    min_w, min_h = 999999999, 999999999
    for y in range(h):
        for x in range(w):
            nx = int((x-a)*__cos - (y-b)*__sin + a)
            ny = int((x-a)*__sin + (y-b)*__cos + b)
            if nx > max_w: max_w = nx+2
            if ny > max_h: max_h = ny+2
            if nx < min_w: min_w = nx
            if ny < min_h: min_h = ny
            img_list.append((x, y, nx, ny))
    new_img = zeros((max_h-min_h, max_w-min_w, c), dtype=uint8)
    for x, y, nx, ny in img_list:
        if not ( max_h-min_h > ny-min_h > 0 and max_w-min_w > nx-min_w > 0 ): continue
        new_img[ny-min_h, nx-min_w] = img[y, x]
    auto_smooth_fill(new_img)
    #new_img = fit_image(new_img)
    return new_img
@jit
def stack_img(img:ndarray, stack:ndarray, pos:Tuple[int, int])->ndarray:
    "write img 'stack' on img 'img' considering of alpha channel"
    pos = (int(pos[0]), int(pos[1]))
    h, w, c = stack.shape
    for y in range(h):
        for x in range(w):
            nx, ny = pos[0]+x, pos[1]+y
            if nx<0 or ny<0: continue
            if ny >= img.shape[1]-1 or nx >= img.shape[0]-1 or ny < 0 or nx < 0: continue
            if y >= stack.shape[1]-1 or x >= stack.shape[0]-1 or y < 0 or x < 0: continue
            b, g, r, a = img[ny, nx]
            b2, g2, r2, a2 = stack[y, x]
            alpha = a2/255
            img[ny, nx] = [int(b2*alpha+b*(1-alpha)), int(g2*alpha+g*(1-alpha)), int(r2*alpha+r*(1-alpha)), 255]
    return img
window = Tk()
window.withdraw()
fake_focus_in = window.focus
AllUUID:List[str] = []
DataDict:Dict[str, Any] = {}
UIDict:Dict[str, Any] = {}
MotionMetaLib:Dict[str, Any] = {}
GlobalData:Dict[str, Any] = {
    "img.error":PhotoImage(file=folder+"res\\image\\error.png"),
    "img.x":PhotoImage(file=folder+"res\\image\\x.png"),
    "img.check":PhotoImage(file=folder+"res\\image\\check.png"),

    "font.noto.ui":Font(family=folder+"res\\font\\NotoSansKR-Medium.otf", size=10),
    "font.noto.ui.sliant":Font(family=folder+"res\\font\\NotoSansKR-Medium.otf", size=10, slant=ITALIC),
    "font.noto.ui.bold":Font(family=folder+"res\\font\\NotoSansKR-Medium.otf", size=10, weight=BOLD),
    "font.noto.text14":Font(family=folder+"res\\font\\NotoSansKR-Medium.otf", size=14, weight=BOLD),

    "license.MotionWriter":(folder+"res\\license\\MotionWriter.txt", "8486a10c4393cee1c25392769ddd3b2d6c242d6ec7928e1414efff7dfb2f07ef"),
    "license.Google Open Font":(folder+"res\\license\\Google Open Font.txt", "02d198273c4badb4046f253170297fb3eb3b38dd6c7b445c3c4a53f21bee360e"),

    "functions": {
        "image.imread": imread,
        "image.show": cv2.imshow,
        "image.rotate": lambda img, center, seta: rotate(img, tuple(center), seta),
        "image.auto_smooth_fill": auto_smooth_fill,

        "math.sin": sin,
        "math.cos": cos,
        "math.pi": pi,
        "math.__rotated": lambda pos, center, seta: __rotated(tuple(pos), tuple(center), seta)
    }
}
window.option_add("*Font", GlobalData["font.noto.ui"])
def logger(_type: Literal["INFO", "WARN", "ERROR"], _string: str, _code: str, _source: str = "Log", _showUI: bool = False):
    text = "[" + strftime('%H:%M:%S', localtime(time())) + "] ["+_type+"] [" + _source + " :: " + _code +"] " + {True:"\n", False:""}[len(_string.split("\n")) != 1] + _string
    print(text)
    if _showUI: {"ERROR":msgbox.showerror, "WARN":msgbox.showwarning, "INFO":msgbox.showinfo}[_type]("MotionWriter", _source + "\n" + _string + "\n" + "CODE: " + _code)
    if _type == "ERROR": exit()
if not "--debug" in argv:
    def exc_hook(exctype: type, value, traceback):
        text = "Traceback (most recent call last):\n" + " ".join(format_tb(traceback)) + exctype.__name__
        if len(str(value)): text += ": " + str(value)
        logger("ERROR", text, "ERROR_INTERNAL_PYTHON", "InternalError :: PythonError :: " + str(exctype.__name__), True)
    sys.excepthook = exc_hook
del sys

def GetHash(data:str)->str: return sha256(data.encode()).hexdigest()
for key in filter(lambda key: key.startswith("license."), GlobalData.keys()):
    with open(GlobalData[key][0], "r", encoding="utf-8") as f: text = f.read(); hash_256 = GetHash(text)
    if hash_256 == GlobalData[key][1]: GlobalData[key] = text
    else: logger("ERROR", "License data file about " + key.replace("license.", "") + " is modified.", "ERROR_LICENSE_MODIFIED", "DataError :: LicenseError", True)
del text, hash_256
    
class Button(Button):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        fg, bg = self.cget("foreground"), self.cget("background")
        self.config(bd=0, activebackground="#CCE4F7", activeforeground="#000000", relief=SOLID)
        self.bind("<Enter>", lambda event: self.config(fg="#000000", bg="#E5F1FB"))
        self.bind("<Leave>", lambda event: self.config(fg=fg, bg=bg))

class TextButton(Label):
    def __init__(self, container, *args, **kwargs):
        self.command = kwargs["command"] if "command" in kwargs.keys() else lambda event: None
        try: del kwargs["command"]
        except: pass
        super().__init__(container, *args, **kwargs)
        self.config(foreground="#0000FF")
        self.bind("<Enter>", lambda event: self.config(underline=True))
        self.bind("<Leave>", lambda event: self.config(underline=False))
        self.bind("<Button-1>", lambda event: self.command())


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

class SpriteDataSet():
    def __init__(self)->None:
        self.x, self.y = 500, 500 #FIXME remove this
        self.start_time = 0
    
    def __json__(self):
        return {"x":self.x, "y":self.y}
class InputType(Enum):
    Integer = 1
    Float = 2
    String = 3
    Boolean = 4
    File = 5
    Selection = 6
    Pos = 7
class MotionMeta():
    def __init__(self, loc: str, inputs: List[List[Union[str, InputType, List[Any]]]], description: str, onTick) -> None:
        self.loc = loc
        self.inputs = inputs
        self.description = description
        self.onTick = onTick
        self.types = {inputs[i][0]:inputs[i][1] for i in range(len(inputs))}
class MotionData():
    def __init__(self, sprite, meta: MotionMeta, undeletable=False, __uuid:str=None, inputs={}):
        if __uuid != None: self.uuid = __uuid
        else: self.uuid = GetUUID()
        self.sprite = sprite
        self.meta = meta
        self.undeletable = undeletable

        self.start_time = 0
        self.end_time = self.sprite.scene.length if not ( self.meta.loc == "default.SetPosition" and self.undeletable ) else 0
        self.sep_time = 1
        self.hold_time = 1
        self.run_time = 0
        self.__ui_data__:Dict[str, List[Any]] = {}
        self.getInput:Dict[str,Any] = inputs
        for name, input_type, *input_args in self.meta.inputs:
            self.getInput[name] = {
                InputType.Integer:0,
                InputType.Float:0.0,
                InputType.String:"",
                InputType.Boolean:True,
                InputType.File:"C:/",
                InputType.Selection:input_args[0],
                InputType.Pos: [n//2 for n in self.sprite.scene.project.video_size]
            }[input_type]

        DataDict[self.uuid] = self
        UIDict[self.uuid] = MotionUI(self.uuid)
        self.sprite.add_motion(self)
    def __json__(self):
        self.reload_input()
        json = {
            "meta": self.meta.loc,
            "uuid": self.uuid,
            "inputs": self.getInput,
            "undeletable": self.undeletable,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "sep_time": self.sep_time,
            "hold_time": self.hold_time
        }
        return json
    def reload_input(self):
        [f() for f in self.UI.getFunc]
    @property
    def UI(self): return UIDict[self.uuid]
    def remove(self):
        self.sprite.remove_motion(self)
        del DataDict[self.uuid]
        del UIDict[self.uuid]
    def write(self, image, dataset: SpriteDataSet, tick):
        if tick < self.start_time: return image
        if tick > self.end_time: return image
        if self.sep_time != 1 and (tick-self.start_time) % self.sep_time < self.hold_time: return image
        self.run_time += 1
        print(self.meta.loc)
        img = self.meta.onTick(image, dataset, tick, self.getInput, GlobalData["functions"], (self.start_time, self.end_time, self.sep_time, self.hold_time, self.run_time))
        return img

class MotionUI():
    def __init__(self, uuid:str) -> None:
        self.uuid = uuid
        self.getFunc: List[FunctionType] = []
    def meta_draw(self):
        frame = Frame(self.frame_repos)
        frame.pack(side=TOP, fill=BOTH)
        line = 1
        for name, input_type, *input_args in self.data.meta.inputs:
            Label(frame, text=name+":").grid(row=line, column=1, sticky=W)
            if input_type == InputType.Integer:
                var = StringVar(value=0)
                try: 
                    if input_args[-1] != None: var.set(input_args[-1])
                except: pass
                entry = Entry(frame, textvariable=var)
                entry.grid(row=line, column=2, sticky=W)
                def done(event, var, data, name):
                    fake_focus_in()
                    try: data.getInput[name] = round(float(var.get()))
                    except: data.getInput[name] = 0
                    var.set(data.getInput[name])
                entry.bind("<Return>", partial(done, var=var, data=self.data, name=name))
                self.getFunc.append(partial(done, event=None, var=var, data=self.data, name=name))
            elif input_type == InputType.Float:
                var = StringVar(value=0)
                try: 
                    if input_args[-1] != None: var.set(input_args[-1])
                except: pass
                entry = Entry(frame, textvariable=var)
                entry.grid(row=line, column=2, sticky=W)
                def done(event, var, data, name):
                    fake_focus_in()
                    try: data.getInput[name] = float(var.get())
                    except: data.getInput[name] = 0
                    var.set(data.getInput[name])
                entry.bind("<Return>", partial(done, var=var, data=self.data, name=name))
                self.getFunc.append(partial(done, event=None, var=var, data=self.data, name=name))
            elif input_type == InputType.String:
                var = StringVar()
                try: 
                    if input_args[-1] != None: var.set(input_args[-1])
                except: pass
                entry = Entry(frame, textvariable=var)
                entry.grid(row=line, column=2, sticky=W)
                def done(event, var, data, name):
                    fake_focus_in()
                    data.getInput[name] = var.get()
                entry.bind("<Return>", partial(done, var=var, data=self.data, name=name))
                self.getFunc.append(partial(done, event=None, var=var, data=self.data, name=name))
            elif input_type == InputType.Boolean:
                var = StringVar()
                try: 
                    if input_args[-1] != None: var.set(input_args[-1])
                except: pass
                def done(data, name, selected):
                    fake_focus_in()
                    data.getInput[name] = {"true":True, "false":False}[selected]
                OptionMenu(frame, var, "true", *("true", "false"), command=partial(done, data=self.data, name=name)).grid(row=line, column=2, sticky=W)
                self.getFunc.append(partial(done, data=self.data, name=name))
            elif input_type == InputType.File:
                label = Label(frame, text="C:/", font="TkDefaultFont")
                try: 
                    if input_args[-1] != None: label.config(text=input_args[-1])
                except: pass
                label.grid(row=line, column=2, sticky=W)
                def done(data, name, label, setOf=False):
                    fake_focus_in()
                    if setOf: data.getInput[name] = askopenfilename(filetypes=(("All Files", "*.*"),))
                    else: data.getInput[name] = label.cget("text")
                    label.config(text=data.getInput[name])
                Button(frame, text="...", command=partial(done, data=self.data, name=name, label=label, setOf=True)).grid(row=line, column=3, sticky=W)
                self.getFunc.append(partial(done, data=self.data, name=name, label=label))
                #self.getFunc.append(partial(done, data=self.data, name=name, label=label))
                #Because this is a file input, which is automatically updated, we don't need to add a function to the getFunc list
                #If we do that, we'll have to set a file each time we make a new video file
            elif input_type == InputType.Selection:
                var = StringVar()
                try: 
                    if input_args[-1] != None: var.set(input_args[0])
                except: pass
                def done(selected, data, name):
                    fake_focus_in()
                    data.getInput[name] = selected
                OptionMenu(frame, var, input_args[0], *input_args, command=partial(done, data=self.data, name=name)).grid(row=line, column=2, sticky=W)
                self.getFunc.append(partial(done, data=self.data, name=name))
            elif input_type == InputType.Pos:
                varx = StringVar(value=0)
                vary = StringVar(value=0)
                try: 
                    if input_args[-1] != None: varx.set(input_args[-1][0]); vary.set(input_args[-1][1])
                except: pass
                frame_entry = Frame(frame)
                frame_entry.grid(row=line, column=2, sticky=W)
                Label(frame_entry, text="[").pack(side=LEFT)
                entryx = Entry(frame_entry, textvariable=varx, width=6)
                entryx.pack(side=LEFT)
                Label(frame_entry, text=", ").pack(side=LEFT)
                entryy = Entry(frame_entry, textvariable=vary, width=6)
                entryy.pack(side=LEFT)
                Label(frame_entry, text="]").pack(side=LEFT)
                def done(event, var, data, name, slot):
                    fake_focus_in()
                    try: data.getInput[name][slot] = round(float(var.get()))
                    except: data.getInput[name][slot] = 0
                    var.set(data.getInput[name][slot])
                entryx.bind("<Return>", partial(done, var=varx, data=self.data, name=name, slot=0))
                entryy.bind("<Return>", partial(done, var=vary, data=self.data, name=name, slot=1))
                self.getFunc.append(partial(done, event=None, var=varx, data=self.data, name=name, slot=0))
                self.getFunc.append(partial(done, event=None, var=vary, data=self.data, name=name, slot=1))

            line += 1
    @property
    def data(self)->MotionData: return DataDict[self.uuid]
    def draw(self):
        self.frame = Frame(self.data.sprite.UI.frame_sprite_edit_motion, bg="#FFFFFF")
        self.frame.pack(fill=X, padx=5, pady=10)
        self.frame_repos = Frame(self.frame)
        self.frame_repos.pack(side=LEFT)
        self.frame_up = Frame(self.frame_repos)
        self.frame_up.pack(fill="x")
        self.label_meta_loc = Label(self.frame_up, text=self.data.meta.loc, font=GlobalData["font.noto.ui.sliant"])
        self.label_meta_loc.pack(side="left")
        if not self.data.undeletable:
            self.btn_delete = Button(self.frame_up, text="X", command=self.remove)
            self.btn_delete.pack(side="right")
        
        self.var_start = StringVar(value=self.data.start_time)
        self.var_end   = StringVar(value=self.data.end_time)
        self.var_sep   = StringVar(value=self.data.sep_time)
        self.var_hold  = StringVar(value=self.data.hold_time)
        self.frame_run_info = Frame(self.frame_repos)
        self.frame_run_info.pack(fill="x")
        self.entry_start = Entry(self.frame_run_info, textvariable=self.var_start, width=4)
        self.entry_start.pack(side="left")
        Label(self.frame_run_info, text="ticks(s)  to  ",   font=GlobalData["font.noto.ui.sliant"]).pack(side="left")
        self.entry_end = Entry(self.frame_run_info, textvariable=self.var_end, width=4)
        self.entry_end.pack(side="left")
        Label(self.frame_run_info, text="tick(s)  each  ",  font=GlobalData["font.noto.ui.sliant"]).pack(side="left")
        self.entry_sep = Entry(self.frame_run_info, textvariable=self.var_sep, width=4)
        self.entry_sep.pack(side="left")
        Label(self.frame_run_info, text="tick(s)  holds  ", font=GlobalData["font.noto.ui.sliant"]).pack(side="left")
        self.entry_hold = Entry(self.frame_run_info, textvariable=self.var_hold, width=4)
        self.entry_hold.pack(side="left")
        Label(self.frame_run_info, text="tick(s)", font=GlobalData["font.noto.ui.sliant"]).pack(side="left")

        
        def done_start(e, var, data):
            fake_focus_in()
            try: data.start_time = round(float(var.get()))
            except: data.start_time = 0
            var.set(data.start_time)
        def done_end(e, var, data):
            fake_focus_in()
            try: data.end_time = round(float(var.get()))
            except: data.end_time = 0
            var.set(data.end_time)
        def done_sep(e, var, data):
            fake_focus_in()
            try: data.sep_time = round(float(var.get()))
            except: data.sep_time = 0
            var.set(data.sep_time)
        def done_hold(e, var, data):
            fake_focus_in()
            try: data.hold_time = round(float(var.get()))
            except: data.hold_time = 0
            var.set(data.hold_time)
        self.getFunc    .append(            partial(done_start, e=None, var=self.var_start, data=self.data))
        self.getFunc    .append(            partial(done_end  , e=None, var=self.var_end  , data=self.data))
        self.getFunc    .append(            partial(done_sep  , e=None, var=self.var_sep  , data=self.data))
        self.getFunc    .append(            partial(done_hold , e=None, var=self.var_hold , data=self.data))
        self.entry_start.bind  ("<Return>", partial(done_start,         var=self.var_start, data=self.data))
        self.entry_end  .bind  ("<Return>", partial(done_end  ,         var=self.var_end  , data=self.data))
        self.entry_sep  .bind  ("<Return>", partial(done_sep  ,         var=self.var_sep  , data=self.data))
        self.entry_sep  .bind  ("<Return>", partial(done_hold ,         var=self.var_hold , data=self.data))
        self.meta_draw()
    def remove(self):
        self.data.remove()
        for obj in self.__dict__:
            try: self.__getattribute__(obj).destroy()
            except: pass
class SpriteData():
    def __init__(self, scene, name:str, __uuid:str=None, autoAddDefaultMotion=True) -> None:
        if __uuid != None: self.uuid = __uuid
        else: self.uuid = GetUUID()
        self.scene = scene
        self.init_name = name
        self.image = None
        self.motions:List[MotionData] = []
        self.dataset:SpriteDataSet = SpriteDataSet()

        DataDict[self.uuid] = self
        UIDict[self.uuid] = SpriteUI(self.uuid)
        self.scene.add_sprite(self)

        if autoAddDefaultMotion:
            MotionData(self, MotionMetaLib["default.ImageLoader"], undeletable=True)
            MotionData(self, MotionMetaLib["default.SetPosition"], undeletable=True)
    def __json__(self):
        json = {
            "name": self.UI.name,
            "uuid": self.uuid,
            "dataset": self.dataset.__json__(),
            "motions": {}
        }
        for motion in self.motions:
            json["motions"][motion.uuid] = motion.__json__()
        return json
    def draw(self):
        self.UI.draw()
    def add_motion(self, motion:MotionData):
        self.motions.append(motion)
        motion.UI.draw()
        self.UI.frame_motion_add_start.pack_forget()
        self.UI.frame_motion_add_start.pack(fill=X, padx=5)
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
    def write(self, tick, image, dataset):
        def work_motion(sprite, img, dataset, tick, __sprite_num=0):
            if __sprite_num > len(sprite.motions)-1: return img
            sprite.motions[__sprite_num].reload_input()
            img = sprite.motions[__sprite_num].write(img, dataset, tick)
            return work_motion(sprite, img, dataset, tick, __sprite_num+1)
        loaded = work_motion(self, zeros((1, 1, 4), dtype=uint8), dataset, tick)
        #cv2.imshow("Sprite", loaded)
        #cv2.waitKey()
        shape = loaded.shape
        new_x_zero = dataset.x - shape[1]//2
        new_y_zero = dataset.y - shape[0]//2
        #print(self.x, self.y, shape)
        print(image.shape, loaded.shape, new_x_zero, new_y_zero)
        image = stack_img(image, loaded, (new_x_zero, new_y_zero))
        # for x in range(shape[1]):
        #     for y in range(shape[0]):
        #         try: image[new_y_zero+y, new_x_zero+x] = loaded[y, x]
        #         except: pass
        #cv2.imshow("Sprite", image)
        return image

class SpriteUI():
    def __init__(self, uuid:str) -> None:
        self.uuid = uuid

        self.frame_sprite_list = Frame(self.data.scene.UI.frame_sprite_list, bg="#FFFFFF", cursor="hand2")
        self.frame_sprite_list.pack(fill=X, side=TOP)
        self.frame_sprite_list.bind("<Button-1>", lambda o: self.focus())
        self.entry_sprite_name_list = Entry(self.frame_sprite_list)
        self.entry_sprite_name_list.insert(END, self.data.init_name)
        self.entry_sprite_name_list.pack(side=LEFT)
        self.entry_sprite_name_list.bind("<Return>", lambda o: self.focus())
        self.btn_sprite_remove = Button(self.frame_sprite_list, image=GlobalData["img.x"], bg="#FFFFFF", relief=SOLID, bd=0, command=self.remove)
        self.btn_sprite_remove.pack(side=RIGHT, padx=40)
    def remove(self):
        isok = self.data.remove()
        if not isok: logger("WARN", "Scene must have at least 1 sprite", "WARN_SPRITE_REMOVE", "InteractionWarn :: SpriteWarn", True); return
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

        self.frame_motion_add_start = Frame(self.frame_sprite_edit_motion, bg="#FFFFFF")
        self.frame_motion_add_start.pack(fill=X, padx=5)
        self.btn_motion_add_start = Button(self.frame_motion_add_start, text="새 모션 추가", command=self.add_motion, bg="#FFFFFF", font=GlobalData["font.noto.ui.bold"])
        self.btn_motion_add_start.pack(side=LEFT)
    def focus(self):
        fake_focus_in()
        self.label_sprite_info.config(text="The motions of sprite \""+self.name+"\"")

        [sprite.UI.unfocus() for sprite in self.data.scene.sprites]
        self.frame_sprite_list.config(bg="#F0F0F0")
        self.btn_sprite_remove.config(bg="#F0F0F0")
        self.frame_sprite_edit.place(x=0, y=0, relwidth=1, relheight=0.99)
    def unfocus(self):
        self.frame_sprite_list.config(bg="#FFFFFF")
        self.btn_sprite_remove.config(bg="#FFFFFF")
        self.frame_sprite_edit.place_forget()
    def add_motion(self):
        self.tk_add_motion = Toplevel()
        self.tk_add_motion.title("새 모션 추가")
        self.tk_add_motion.geometry("450x225")
        #self.tk_add_motion.resizable(False, False)
        self.frame_add_frame_search = Frame(self.tk_add_motion, bg="#FFFFFF")
        self.frame_add_frame_search.pack(fill=X)
        self.entry_add_motion_search = Entry(self.frame_add_frame_search)
        self.entry_add_motion_search.pack(fill=X)
        self.frame_add_motion_list = ScrollableFrame(self.tk_add_motion, bg="#FFFFFF")
        self.frame_add_motion_list.pack(fill=BOTH, expand=True)
        def reload_motion_list(event, entry, frame:Frame):
            for child in frame.children.values(): child.pack_forget()
            list_motion_name = list(MotionMetaLib.keys())
            search = entry.get()
            if len(search) == 0:
                recommend_motions = list(map(lambda n:(n, 0), list_motion_name))
            else:
                extracted = extract(search, list_motion_name)
                recommend_motions = list(filter(lambda t:t[1]>=75, extracted))
                if len(recommend_motions) == 0: recommend_motions = extracted
            for motion_name, rate in recommend_motions:
                Button(self.frame_add_motion_list, text=motion_name+" ("+str(rate)+"%)", command=partial(self.__add_motion_work, motion_name), bg="#FFFFFF", anchor=W, justify=LEFT).pack(fill=X)
        self.entry_add_motion_search.bind("<KeyRelease>", partial(reload_motion_list, entry=self.entry_add_motion_search, frame=self.frame_add_motion_list))
        reload_motion_list(None, self.entry_add_motion_search, self.frame_add_motion_list)
    def __add_motion_work(self, motion_name):
        MotionData(self.data, MotionMetaLib[motion_name])
        self.tk_add_motion.destroy()

class SceneData():
    def __init__(self, project, name:str, length:int, __uuid=None, __auto_sprite=True) -> None:
        self.project = project
        self.name = name
        self.length = length
        if __uuid != None: self.uuid = __uuid
        else: self.uuid = GetUUID()

        self.sprites:List[SpriteData] = []

        DataDict[self.uuid] = self

        UIDict[self.uuid] = SceneUI(self.uuid)
        self.project.add_scene(self)
        if __auto_sprite: SpriteData(self, "New Sprite")
    def __json__(self):
        json = {
            "name": self.name,
            "length": self.length,
            "uuid": self.uuid,
            "sprites": {}
        }
        for sprite in self.sprites:
            json["sprites"][sprite.UI.name] = sprite.__json__()
        return json
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
    def write(self, writer):
        size = self.project.video_size
        copied_dataset = {}
        for sprite in self.sprites: copied_dataset[sprite.uuid] = deepcopy(sprite.dataset)
        r = list(range(self.length))
        for i, tick in enumerate(r):
            tick_image = zeros((size[1], size[0], 4), dtype=uint8)
            tick_image[:, :, :3] = 255
            for sprite in self.sprites:
                tick_image = sprite.write(tick, tick_image, copied_dataset[sprite.uuid])
            writer.write(cv2.cvtColor(tick_image, cv2.COLOR_BGRA2BGR))
            self.project.UI.update_extract_progress_sprite(int((i+1) / len(r) * 100))
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

        self.frame_split_left = Frame(self.frame, bg="#FFFFFF")
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
        self.addNewSpriteFrame = Frame(self.frame_sprite_list, bg="#FFFFFF")
        self.addNewSpriteFrame.pack(fill=X)
        self.addNewSpriteBtn = Button(self.addNewSpriteFrame, text="새로운 스프라이트 추가", command=self.add_sprite, bg="#FFFFFF", font=GlobalData["font.noto.ui.bold"])
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
    def __init__(self, name:str="untitled", video_size=(1000, 1000), loc=None, __uuid=None) -> None:
        self.name = name
        self.loc = loc
        self.saved = loc != None
        if __uuid != None: self.uuid = __uuid
        else: self.uuid = GetUUID()
        self.video_size = video_size
        DataDict[self.uuid] = self

        self.scenes:List[SceneData] = []

        
        global UIDict
        UIDict = {self.uuid:ProjectUI(self.uuid)}
    def draw(self):
        #[scene.draw() for scene in self.scenes]
        self.UI.draw()
    def add_scene(self, scene: SceneData):
        self.scenes.append(scene)
        scene.draw()
        scene.UI.focus()
        self.UI.addNewSceneBtn.pack_forget()
        self.UI.addNewSceneBtn.pack(side=LEFT, padx=5)
    @property
    def UI(self): return UIDict[self.uuid]
    def __json__(self):
        json =  {
            "name": self.name,
            "uuid": self.uuid,
            "video_size": self.video_size,
            "scenes": {}
        }
        for scene in self.scenes:
            json["scenes"][scene.name] = scene.__json__()
        return json
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

        self.addNewSceneBtn = Button(self.sceneBarFrame, text="+", width=2, command=self.add_scene)

        self.workspace = Frame(self.screen, bg="#FFFFFF")
        self.workspace.place(x=0, y=50, relwidth=1, height=self.y-60)

        menubar=Menu(window)

        file_help=Menu(menubar, tearoff=0)
        file_help.add_command(label = "새로 만들기")
        file_help.add_command(label = "불러오기", command = self.load)
        file_help.add_command(label = "저장하기")
        file_help.add_command(label = "다른 이름으로 저장하기", command=self.save_as_new_name)
        file_help.add_separator()
        file_help.add_command(label = "내보내기", command=self.extract)
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

        self.extract_path = StringVar(value="C:/Users/USER/Desktop/test.avi") #FIXME remove this
    def close(self):
        if not self.data.saved:
            msgbox.askyesno("MotionWriter", "저장하지 않았습니다. 저장하시겠습니까?")
            self.save_auto()
        window.destroy()
    def save_auto(self):
        pass
        #if self.data.loc != None:
    def load(self):
        filename = askopenfilename(filetypes=(("Motion Writer Project", "*.mwp"), ("All Files", "*.*")))
        if not filename.endswith(".mwp"): return logger("WARN", "Not a Motion Writer Project", "IS_NOT_A_MWP", "InteractionWarn :: TypeWarn")
        if filename == "": return
        self.close()
        start_sub(filename)
    def extract(self):
        self.win_extract = Toplevel(window)
        self.win_extract.title("내보내기")
        self.win_extract.geometry("500x300")
        self.win_extract.resizable(False, False)
        self.win_extract.bind("<Escape>", lambda e: self.win_extract.withdraw())
        #self.win_extract.option_add("*Foreground", "#FFFFFF")
        #self.win_extract.option_add("*Background", "#383f49")
        #self.win_extract.option_add("*Background", "#FFFFFF")
        frame = Frame(self.win_extract, bg="#FFFFFF")
        frame.pack(fill=BOTH, expand=True)

        frame_button = Frame(frame, bg="#FFFFFF")
        frame_button.pack(side=BOTTOM, fill=X, pady=15, padx=15)
        btn_next_or_done = Button(frame_button, text="다음 >", bg="#FFFFFF")
        btn_next_or_done.pack(side=RIGHT, padx=10)
        #btn_prev_or_cancel = Button(frame_button, text="취소")
        #btn_prev_or_cancel.pack(side=RIGHT, padx=10)

        frame_process_position = Frame(frame, bg="#FFFFFF")
        frame_process_position.pack(side=TOP, fill=X, pady=15, padx=15)
        frame_process = Frame(frame_process_position, bg="#FFFFFF")
        frame_process.pack()
        label_process_1 = Label(frame_process, text="동영상 정보 설정", font=GlobalData["font.noto.ui.bold"], bg="#FFFFFF")
        label_process_1.pack(side=LEFT, padx=5)
        Label(frame_process, text=">", font=GlobalData["font.noto.text14"], fg="#c0c0c0", bg="#FFFFFF").pack(side=LEFT, padx=5)#, fg="#00a000"
        label_process_2 = Label(frame_process, text="동영상 추출", font=GlobalData["font.noto.ui.bold"], state=DISABLED, bg="#FFFFFF")
        label_process_2.pack(side=LEFT, padx=5)
        Label(frame_process, text=">", font=GlobalData["font.noto.text14"], fg="#c0c0c0", bg="#FFFFFF").pack(side=LEFT, padx=5)#, fg="#00a000"
        label_process_3 = Label(frame_process, text="동영상 추출 완료", font=GlobalData["font.noto.ui.bold"], state=DISABLED, bg="#FFFFFF")
        label_process_3.pack(side=LEFT, padx=5)

        main_frame = Frame(frame, bg="#FFFFFF")
        main_frame.pack(fill=BOTH, expand=True, padx=15)

        frame_save_info = Frame(main_frame, bg="#FFFFFF")
        # frame_save_type = Frame(frame_save_info)
        # label_save_type = Label(frame_save_type, text="파일 확장자", font=GlobalData["font.noto.ui.bold"], anchor=W)
        # label_save_type.pack(fill=X, side=TOP, padx=3)
        # intVar = IntVar()
        # radio_save_type_mp4 = Radiobutton(frame_save_type, image=GlobalData["img.btn-mp4"], compound=TOP, overrelief=SOLID, indicatoron=False, variable=intVar, value=1, relief=SOLID, bd=0, selectcolor="#404040")
        # radio_save_type_mp4.pack(side=LEFT, padx=45)
        # radio_save_type_avi = Radiobutton(frame_save_type, image=GlobalData["img.btn-avi"], compound=TOP, overrelief=SOLID, indicatoron=False, variable=intVar, value=2, relief=SOLID, bd=0, selectcolor="#404040")
        # radio_save_type_avi.pack(side=LEFT, padx=45)
        # radio_save_type_gif = Radiobutton(frame_save_type, image=GlobalData["img.btn-gif"], compound=TOP, overrelief=SOLID, indicatoron=False, variable=intVar, value=3, relief=SOLID, bd=0, selectcolor="#404040")
        # radio_save_type_gif.pack(side=LEFT, padx=45)
        frame_save_loc = Frame(frame_save_info, bg="#FFFFFF")
        frame_save_loc.pack(fill=X, expand=True)
        label_save_loc = Label(frame_save_loc, text="저장 위치", font=GlobalData["font.noto.ui.bold"], anchor=W, bg="#FFFFFF")
        label_save_loc.pack(fill=X, side=TOP, padx=3)
        entry_save_loc = Label(frame_save_loc, width=52, bd=1, relief=SOLID, anchor=W, text="C:/Users/USER/Desktop/test.avi", bg="#FFFFFF")#"C:/"+self.data.name+".gif" #FIXME remove this
        entry_save_loc.pack(side=LEFT, padx=5)
        btn_save_loc = Button(frame_save_loc, text="...", bg="#FFFFFF")
        btn_save_loc.pack(side=LEFT, padx=5)
        def select_save_loc(entry:Entry):
            self.extract_path.set(asksaveasfilename(filetypes=(("비디오 파일", ".mp4 .avi .gif"), ("모든 파일", "*.*"))))
            entry.config(text=self.extract_path.get())
            self.win_extract.focus()
        btn_save_loc.config(command=partial(select_save_loc, entry_save_loc))

        frame_working_info = Frame(main_frame, bg="#FFFFFF")
        frame_working_info_scene = Frame(frame_working_info, bg="#FFFFFF")
        frame_working_info_scene.pack(fill=X, expand=True)
        label_working_info_scene = Label(frame_working_info_scene, text="장면 :: 0%", font=GlobalData["font.noto.ui.bold"], anchor=W, bg="#FFFFFF")
        label_working_info_scene.pack(fill=X, padx=3, pady=10)
        progress_bar_scene = Progressbar(frame_working_info_scene, orient=HORIZONTAL, mode="determinate", maximum=100)
        progress_bar_scene.pack(fill=X)
        frame_working_info_sprite = Frame(frame_working_info, bg="#FFFFFF")
        frame_working_info_sprite.pack(fill=X, expand=True)
        label_working_info_sprite = Label(frame_working_info_sprite, text="스프라이트 :: 0%", font=GlobalData["font.noto.ui.bold"], anchor=W, bg="#FFFFFF")
        label_working_info_sprite.pack(fill=X, padx=3, pady=10)
        progress_bar_sprite = Progressbar(frame_working_info_sprite, orient=HORIZONTAL, mode="determinate", maximum=100)
        progress_bar_sprite.pack(fill=X)
        def __update_scene(rate, label, progress_bar):
            label.config(text=f"장면 :: {rate}%")
            progress_bar.config(value=rate)
            progress_bar.update()
        def __update_sprite(rate, label, progress_bar):
            label.config(text=f"스프라이트 :: {rate}%")
            progress_bar.config(value=rate)
            progress_bar.update()
        self.update_extract_progress_scene  = partial(__update_scene,  label=label_working_info_scene,  progress_bar=progress_bar_scene)
        self.update_extract_progress_sprite = partial(__update_sprite, label=label_working_info_sprite, progress_bar=progress_bar_sprite)

        frame_done_info = Frame(main_frame, bg="#FFFFFF")
        Label(frame_done_info, text="\n",                     bg="#FFFFFF").pack()
        Label(frame_done_info, image=GlobalData["img.check"], bg="#FFFFFF").pack()
        Label(frame_done_info, text="당신의 환상적인 동영상이 정삳적으로 추출되었습니다.", font=GlobalData["font.noto.ui.bold"], anchor=W, bg="#FFFFFF").pack()
        self.label_done_path = Label(frame_done_info, text="위치 :: C:/Users/USER/Desktop/test.avi", font=GlobalData["font.noto.ui"], anchor=W, bg="#FFFFFF")
        frame_done_link = Frame(frame_done_info, bg="#FFFFFF")
        frame_done_link.pack()
        Label(frame_done_link, text="당신의 환상적인 동영상을 확인하려면 ", font=GlobalData["font.noto.ui.sliant"], anchor=W, bg="#FFFFFF").pack(side=LEFT)
        def open_video(self): __import__("os").startfile(self.extract_path.get())
        TextButton(frame_done_link, text="여기", font=GlobalData["font.noto.ui.bold"], anchor=W, bg="#FFFFFF", cursor="hand2", command=partial(open_video, self)).pack(side=LEFT)
        Label(frame_done_link, text="를 클릭하세요.", font=GlobalData["font.noto.ui.sliant"], anchor=W, bg="#FFFFFF").pack(side=LEFT)


        self.extract_win_mode = 0
        packs = [
            lambda: frame_save_info.pack(fill=BOTH, expand=True),
            lambda: frame_working_info.pack(fill=BOTH),
            lambda: frame_done_info.pack()
        ]
        packs[0]()
        def next_or_done(btn_next_or_done, frames, labels, packs):
            self.win_extract.focus()
            self.extract_win_mode += 1
            if self.extract_win_mode >= 0: btn_next_or_done.config(text = "다음 >")
            if self.extract_win_mode == 1: btn_next_or_done.config(state= DISABLED)
            else:                          btn_next_or_done.config(state= NORMAL)
            if self.extract_win_mode >= 2: btn_next_or_done.config(text = "마침")
            if self.extract_win_mode >= 3: self.win_extract.destroy(); return
            [label.config(state=DISABLED) for label in labels]
            labels[self.extract_win_mode].config(state=NORMAL)
            for frame in frames: frame.pack_forget(); frame.update()
            packs[self.extract_win_mode]()
            if self.extract_win_mode == 1: self.__extract(partial(next_or_done, btn_next_or_done, frames, labels, packs))
            self.win_extract.focus()
        btn_next_or_done.config(command=partial(next_or_done, btn_next_or_done, [frame_save_info, frame_working_info, frame_done_info], [label_process_1, label_process_2, label_process_3], packs))
        self.win_extract.deiconify()
    def __extract(self, end_command):
        print("동영상 추출!", self.extract_path.get())
        writer = cv2.VideoWriter(self.extract_path.get(), cv2.VideoWriter_fourcc(*'DIVX'), 20, self.data.video_size)
        for n, scene in enumerate(self.data.scenes):
            print(n, scene)
            scene.write(writer)
            self.update_extract_progress_scene((n+1)/len(self.data.scenes)*100)
        writer.release()
        end_command()
    def save_as_new_name(self):
        loc = asksaveasfilename(title="Save As..", filetypes=[("MotionWriterProject", "*.mwp")])
        self.__save(loc)
    def __save(self, loc: str):
        if not loc.endswith(".mwp"): loc += ".mwp"
        with open(loc, "w") as file:
            dump(self.data.__json__(), file, indent=4)
    def open_win_license(self, __type):
        self.win_license.deiconify()
        self.win_license.title("MotionWriter :: License :: " + __type.replace("license.", ""))
        try: self.label_license.destroy()
        except: ...
        self.label_license = Label(self.frame_license, text=GlobalData[__type], justify=LEFT)
        self.label_license.pack(fill=BOTH)
        self.frame_license.update_ui()
    def add_scene(self, name="", tick="100", option="tick(s)   "):
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
        self.var_scene_maker_tick = StringVar()
        self.option_scene_maker_tick = OptionMenu(self.frame_scene_maker_tick, self.var_scene_maker_tick, option, "tick(s)   ", "second(s)")
        self.entry_scene_maker_tick = Entry(self.frame_scene_maker_tick, width=14)
        self.entry_scene_maker_tick.insert(END, tick)
        self.label_scene_maker_tick.pack(fill=X, ipady=2)
        self.frame_scene_maker_tick.pack()
        self.option_scene_maker_tick.pack(side=RIGHT)
        self.entry_scene_maker_tick.pack(side=LEFT)
        self.frame_scene_maker_btn = Frame(self.tk_scene_maker)
        self.btn_scene_maker_done = Button(self.frame_scene_maker_btn, text="Done", command=self.__add_scene_done)
        self.btn_scene_maker_exit = Button(self.frame_scene_maker_btn, text="Exit", command=self.tk_scene_maker.destroy)
        self.frame_scene_maker_btn.pack(fill=X, ipady=20)
        self.btn_scene_maker_done.pack(side=LEFT)
        self.btn_scene_maker_exit.pack(side=RIGHT)
    def __add_scene_done(self):
        name, tick, option = self.entry_scene_maker_name.get(), self.entry_scene_maker_tick.get(), self.var_scene_maker_tick.get()
        self.tk_scene_maker.destroy()
        if len(name) > 10: logger("WARN", "name is too long\nname must be shorter or same 10 letters", "WARN_LENGTH_LIMIT", "ObjectHandleWarn :: SceneWarn", True); return self.add_scene(name)
        if "" in (name.replace(" ", ""), tick): logger("WARN", "you must fill all text box", "WARN_INPUT_EMPTY", "ObjectHandleWarn :: SceneWarn", True); return self.add_scene(name, tick, option)
        try: tick = int(tick)
        except: msgbox.showwarning("New Scene", tick+" isn't a number"); return self.add_scene(name, tick, option)
        if option == "second(s)": tick *= 20 
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

# Import All MotionMeta
__type_dict: Dict[str, InputType] = {
    "Integer":InputType.Integer,
    "Float":InputType.Float,
    "String":InputType.String,
    "Boolean":InputType.Boolean,
    "File":InputType.File,
    "Selection":InputType.Selection,
    "Pos":InputType.Pos,
}
for package_name in listdir(folder+"script"):
    file_path = folder+"script\\"+package_name
    if not is_zipfile(file_path): continue
    with ZipFile(file_path, "r") as zip_file:
        for f in zip_file.filelist:
            if not f.is_dir(): continue
            try:
                init = loads(zip_file.read(f.filename+"__init__.json"))
                name = package_name.split(".")[0] + "." + init["name"]
                inputs:Dict = init["inputs"]
                description:str = init["description"]
                covered_inputs:Tuple[Tuple[str, InputType, Tuple[Any, ...]], ...] = []
                for input_name, [input_type, *input_args] in inputs.items():
                    if len(input_args) == 0: input_args = (None,)
                    covered_inputs += [[input_name, __type_dict[input_type], *input_args],]
                data = {}
                exec(zip_file.read(f.filename+"onTick.py").decode()+"\nfunc = onTick", data)
                onTick = data["func"]
                logger("INFO", "importing "+name, "INFO_IMPORT", "FileReadInfo :: ReadMotionMeta")
                MotionMetaLib[name] = MotionMeta(name, covered_inputs, description, onTick)
            except KeyError as ke: print(ke); continue
try: del __type_dict, package_name, file_path, zip_file, f, init, name, inputs, description, covered_inputs, data, onTick
except: pass

def __load_project(loc:str):
    with open(loc, "rb") as f:
        data = loads(f.read())
        project_name, project_uuid, project_video_size, scenes = data["name"], data["uuid"], data["video_size"], data["scenes"]
        proData = ProjectData(project_name, project_video_size, project_uuid)
        for scene in scenes.values():
            scene_name, scene_uuid, scene_length, sprites = scene["name"], scene["uuid"], scene["length"], scene["sprites"]
            scData = SceneData(proData, scene_name, scene_length, scene_uuid, False)
            for sprite in sprites.values():
                sprite_name, sprite_uuid, sprite_dataset, motions = sprite["name"], sprite["uuid"], sprite["dataset"], sprite["motions"]
                spData = SpriteData(scData, sprite_name, sprite_uuid, False)
                spData.dataset.x, spData.dataset.y = sprite_dataset.values()
                for motion in motions.values():
                    motion_meta, motion_uuid, motion_inputs, motion_undeletable, start, end, sep, hold = motion["meta"], motion["uuid"], motion["inputs"], motion["undeletable"], motion["start_time"], motion["end_time"], motion["sep_time"], motion["hold_time"]
                    meta:MotionMeta = deepcopy(MotionMetaLib[motion_meta])
                    for __type, __value in motion_inputs.items():
                        for i in range(len(meta.inputs)):
                            name, _, *v = meta.inputs[i]
                            if name == __type:
                                meta.inputs[i] += [__value]; break
                        #meta.inputs[__type].value = __value
                    moData = MotionData(spData, meta, bool(motion_undeletable), motion_uuid, motion_inputs)
                    moData.start_time, moData.end_time, moData.sep_time, moData.hold_time = start, end, sep, hold

                    moData.UI.entry_start.delete(0, END)
                    moData.UI.entry_end.delete(0, END)
                    moData.UI.entry_sep.delete(0, END)
                    moData.UI.entry_hold.delete(0, END)
                    moData.UI.entry_start.insert(END, moData.start_time)
                    moData.UI.entry_end.insert(END, moData.end_time)
                    moData.UI.entry_sep.insert(END, moData.sep_time)
                    moData.UI.entry_hold.insert(END, moData.hold_time)

    return proData
try:
    pro = __load_project(list(filter(lambda s: not s.startswith("--"), argv[1:]))[0])
except:
    pro = ProjectData()
    SceneData(pro, "Scene 1", 200)
pro.draw()