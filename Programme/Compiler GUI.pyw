from tkinter import *
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.messagebox import showerror, showinfo
from time import sleep
from threading import Thread
from io import StringIO
import compiler


# updater Thread running in the background: highlights the code and updates the builds displayed in the display frames
class UpdateThread(Thread):

    _stop = False

    def __init__(self):
        super().__init__(target=self.update_action)
        self._stop = False

    def stop(self):
        self._stop = True

    def update_action(self):
        global successful_build, build_oc, build_mn
        mnemonic = ""
        opcode = ""
        while not self._stop:
            sleep(1)

            try:
                assembler_editor.highlight()
            except RuntimeError:
                exit(0)

            try:
                mnemonic, opcode = compiler.compile_code(assembler_editor.get("1.0", END))
                successful_build = True
                # update latest build_oc if successful
                build_oc = opcode
                build_mn = mnemonic
            except (IndexError, compiler.NumberFormatError, compiler.NonExistingInstructionError, compiler.InvalidSyntax):
                successful_build = False
            set_display_frames(mnemonic, opcode)

        exit(0)


# extended text widget capable of highlighting the assembler language
class Editor(Text):

    def __init__(self, *args, **kwargs):
        Text.__init__(self, *args, **kwargs)

    def highlight(self):

        # define tags
        self.tag_configure("inst_tag", foreground="orange", font=("Arial", 11))
        self.tag_configure("comment_tag", foreground="green", font=("Comic Sans MS", 11))
        self.tag_configure("label_tag", foreground="red", font=("Arial", 11))

        self.mark_set("searchLimit", END)

        #  highlight instructions
        for inst in compiler.inst_list:
            self.mark_set("matchStart", "1.0")
            self.mark_set("matchEnd", "1.0")
            count = IntVar()
            while True:
                index = self.search(inst, "matchEnd", "searchLimit", count=count)
                if index == "":
                    break
                if count.get() == 0:
                    break
                self.mark_set("matchStart", index)
                self.mark_set("matchEnd", "%s+%sc" % (index, count.get()))
                self.tag_add("inst_tag", "matchStart", "matchEnd")

        # highlight comments
        self.mark_set("matchStart", "1.0")
        self.mark_set("matchEnd", "1.0")
        while True:
            index = self.search("//", "matchEnd", "searchLimit")
            if index == "":
                break
            self.mark_set("matchStart", index)
            self.mark_set("matchEnd", f"{index} lineend")
            self.tag_add("comment_tag", "matchStart", "matchEnd")

        # highlight labels
        self.mark_set("matchStart", "1.0")
        self.mark_set("matchEnd", "1.0")
        while True:
            index = self.search("#", "matchEnd", "searchLimit")
            if index == "":
                break
            self.mark_set("matchStart", index)
            self.mark_set("matchEnd", f"{index} lineend")
            self.tag_add("label_tag", "matchStart", "matchEnd")


# class for simulating the CPU's behaviour
class CPU(object):

    # instruction set
    def AOUT(self):
        self.carry_flag = self.a_reg > 255
        self.negative_flag = self.a_reg < 0 or self.a_reg & 0b10000000 == 0b10000000
        self.zero_flag = self.a_reg == 0

    def NOOP(self):
        pass

    def LVA(self):
        self.a_reg = self.ram[self.pointer]
        self.pointer += 1

    def LMA(self):
        self.a_reg = self.ram[self.ram[self.pointer]]
        self.pointer += 1

    def LVB(self):
        self.b_reg = self.ram[self.pointer]
        self.pointer += 1

    def LMB(self):
        self.b_reg = self.ram[self.ram[self.pointer]]
        self.pointer += 1

    def LVC(self):
        self.c_reg = self.ram[self.pointer]
        self.pointer += 1

    def LMC(self):
        self.c_reg = self.ram[self.ram[self.pointer]]
        self.pointer += 1

    def ADD(self):
        self.a_reg = self.a_reg + self.ram[self.pointer]
        self.AOUT()
        self.a_reg = self.a_reg & 0xFF
        self.pointer += 1

    def ADDB(self):
        self.a_reg = self.a_reg + self.b_reg
        self.AOUT()
        self.a_reg = self.a_reg & 0xdFF

    def ADDC(self):
        self.a_reg = self.a_reg + self.c_reg
        self.AOUT()
        self.a_reg = self.a_reg & 0xFF

    def SUB(self):
        self.a_reg = self.a_reg - self.ram[self.pointer]
        self.AOUT()
        self.pointer += 1
        self.a_reg = self.a_reg & 0xFF

    def SUBB(self):
        self.a_reg = self.a_reg - self.b_reg
        self.AOUT()
        self.a_reg = self.a_reg & 0xFF

    def SUBC(self):
        self.a_reg = self.a_reg - self.c_reg
        self.AOUT()
        self.a_reg = self.a_reg & 0xFF

    def AND(self):
        self.a_reg = self.a_reg & self.ram[self.pointer]
        self.pointer += 1
        self.AOUT()

    def ANDB(self):
        self.a_reg = self.a_reg & self.b_reg
        self.AOUT()

    def ANDC(self):
        self.a_reg = self.a_reg & self.c_reg
        self.AOUT()

    def OR(self):
        self.a_reg = self.a_reg | self.ram[self.pointer]
        self.pointer += 1
        self.AOUT()

    def ORB(self):
        self.a_reg = self.a_reg | self.b_reg
        self.AOUT()

    def ORC(self):
        self.a_reg = self.a_reg | self.c_reg
        self.AOUT()

    def XOR(self):
        self.a_reg = self.a_reg ^ self.ram[self.pointer]
        self.pointer += 1
        self.AOUT()

    def XORB(self):
        self.a_reg = self.a_reg ^ self.b_reg
        self.AOUT()

    def XORC(self):
        self.a_reg = self.a_reg ^ self.c_reg
        self.AOUT()

    def NOT(self):
        self.a_reg = self.ram[self.pointer] ^ 0xFF
        self.pointer += 1
        self.AOUT()

    def NOTA(self):
        self.a_reg = self.a_reg ^ 0xFF
        self.AOUT()

    def NOTB(self):
        self.a_reg = self.b_reg ^ 0xFF
        self.AOUT()

    def NOTC(self):
        self.c_reg = self.c_reg ^ 0xFF
        self.AOUT()

    def DECAD(self):
        self.a_reg = self.ram[self.ram[self.pointer]] - 1
        self.pointer += 1
        self.AOUT()
        self.a_reg = self.a_reg & 0xFF

    def DEC(self):
        self.a_reg = self.ram[self.pointer] - 1
        self.pointer += 1
        self.AOUT()
        self.a_reg = self.a_reg & 0xFF

    def DECA(self):
        self.a_reg = self.a_reg - 1
        self.AOUT()
        self.a_reg = self.a_reg & 0xFF

    def DECB(self):
        self.a_reg = self.b_reg - 1
        self.AOUT()
        self.a_reg = self.a_reg & 0xFF

    def DECC(self):
        self.a_reg = self.c_reg - 1
        self.AOUT()
        self.a_reg = self.a_reg & 0xFF

    def INCAD(self):
        self.a_reg = self.ram[self.ram[self.pointer]] + 1
        self.AOUT()
        self.pointer += 1
        self.a_reg = self.a_reg & 0xFF

    def INC(self):
        self.a_reg = self.ram[self.pointer] + 1
        self.pointer += 1
        self.AOUT()
        self.a_reg = self.a_reg & 0xFF

    def INCA(self):
        self.a_reg = self.a_reg + 1
        self.AOUT()
        self.a_reg = self.a_reg & 0xFF

    def INCB(self):
        self.a_reg = self.b_reg + 1
        self.AOUT()
        self.a_reg = self.a_reg & 0xFF

    def INCC(self):
        self.a_reg = self.c_reg + 1
        self.AOUT()
        self.a_reg = self.a_reg & 0xFF

    def OUTA(self):
        self.output = self.a_reg

    def OUTB(self):
        self.output = self.b_reg

    def OUTC(self):
        self.output = self.c_reg

    def STA(self):
        self.ram[self.pointer] = self.a_reg
        self.pointer += 1

    def STB(self):
        self.ram[self.pointer] = self.b_reg
        self.pointer += 1

    def STC(self):
        self.ram[self.pointer] = self.c_reg
        self.pointer += 1

    def A2B(self):
        self.b_reg = self.a_reg

    def A2C(self):
        self.c_reg = self.a_reg

    def B2A(self):
        self.a_reg = self.b_reg

    def B2C(self):
        self.c_reg = self.b_reg

    def C2A(self):
        self.a_reg = self.c_reg

    def C2B(self):
        self.b_reg = self.c_reg

    def CMP(self):
        self.carry_flag = (self.a_reg - self.ram[self.pointer]) > 255
        self.negative_flag = self.a_reg - self.ram[self.pointer] < 0
        self.zero_flag = ((self.a_reg - self.ram[self.pointer]) & 0xFF) == 0
        self.pointer += 1

    def CMPB(self):
        self.carry_flag = (self.a_reg - self.b_reg) > 255
        self.negative_flag = (self.a_reg - self.b_reg) < 0
        self.zero_flag = ((self.a_reg - self.b_reg) & 0xFF) == 0

    def CMPC(self):
        self.carry_flag = (self.a_reg - self.c_reg) > 255
        self.negative_flag = (self.a_reg - self.c_reg) < 0
        self.zero_flag = ((self.a_reg - self.c_reg) & 0xFF) == 0

    def JMP(self):
        self.pointer = self.ram[self.pointer]

    def JC(self):
        if self.carry_flag:
            self.pointer = self.ram[self.pointer]
        else:
            self.pointer += 1

    def JN(self):
        if self.negative_flag:
            self.pointer = self.ram[self.pointer]
        else:
            self.pointer += 1

    def JZ(self):
        if self.zero_flag:
            self.pointer = self.ram[self.pointer]
        else:
            self.pointer += 1

    def HLT(self):
        self.halt_flag = True

    def LMAC(self):
        self.a_reg = self.ram[self.c_reg]

    def LMBC(self):
        self.b_reg = self.ram[self.c_reg]

    def LMCC(self):
        self.c_reg = self.ram[self.c_reg]

    def STAC(self):
        self.ram[self.c_reg] = self.a_reg

    def STBC(self):
        self.ram[self.c_reg] = self.b_reg

    def STCC(self):
        self.ram[self.c_reg] = self.c_reg

    def RET(self):
        self.pointer = self.ram[0xFF]

    def CALL(self):
        self.ram[0xFF] = self.pointer + 1
        self.pointer = self.ram[self.pointer + 1]

    execute = {}

    ram = []
    a_reg = 0
    b_reg = 0
    c_reg = 0
    pointer = 0
    output = 0
    carry_flag = False
    negative_flag = False
    zero_flag = False
    halt_flag = False

    def __init__(self, ram_content: list):
        self.ram = ram_content.copy()
        self.execute.update({
            0: self.NOOP,
            1: self.LVA, 2: self.LMA, 3: self.LVB, 4: self.LMB, 5: self.LVC, 6: self.LMC,
            7: self.ADD, 8: self.ADDB, 9: self.ADDC,
            10: self.SUB, 11: self.SUBB, 12: self.SUBC,
            13: self.AND, 14: self.ANDB, 15: self.ANDC,
            16: self.OR, 17: self.ORB, 18: self.ORC,
            19: self.XOR, 20: self.XORB, 21: self.XORC,
            22: self.NOT, 23: self.NOTA, 24: self.NOTB, 25: self.NOTC,
            26: self.DECAD, 27: self.DEC, 28: self.DECA, 29: self.DECB, 30: self.DECC,
            31: self.INCAD, 32: self.INC, 33: self.INCA, 34: self.INCB, 35: self.INCC,
            36: self.AOUT,
            37: self.OUTA, 38: self.OUTB, 39: self.OUTC,
            40: self.STA, 41: self.STB, 42: self.STC,
            43: self.A2B, 44: self.A2C, 45: self.B2A, 46: self.B2C, 47: self.C2A, 48: self.C2B,
            49: self.CMP, 50: self.CMPB, 51: self.CMPC,
            52: self.JMP, 53: self.JC, 54: self.JZ, 55: self.JN,
            56: self.HLT,
            57: self.LMAC, 58: self.LMBC, 59: self.LMCC,
            60: self.STAC, 61: self.STBC, 62: self.STCC,
            254: self.RET, 255: self.CALL})

    # executes the next instruction in ram and returns the callback
    def exec_next(self):
        if not self.halt_flag:
            inst = self.ram[self.pointer]
            self.pointer += 1
            self.execute.get(inst)()

            return "A: " + str(self.a_reg) + "; B: " + str(self.b_reg) + "; C: " + str(self.c_reg) + "\n" \
                   "OUT: " + str(self.output) + "\n" \
                   "POINTER " + str(self.pointer) + "\n" \
                   "Carry: " + str(self.carry_flag) + "; Negative: " + str(self.negative_flag) + ", Zero: " +\
                   str(self.zero_flag) + "\n"
        else:
            return "Halted Execution\n"


# kills the editor root
def kill(_event=None):
    update_thread.stop()
    root.destroy()
    exit(0)


# opens an assembler text file in the editor
def opn():
    global file_name
    assembler_editor.delete(1.0, END)

    file_name = askopenfilename()
    if file_name:
        file = open(file_name, "r")
        assembler_editor.insert(INSERT, file.read())
        file.close()
    else:
        file_name = "/untitled.*"

    root.title("CPU Compiler: " + file_name)


# save the current file in the editor as an assembler text file
def save(_event=None, save_as=False):
    global file_name
    if save_as or file_name == "/untitled.*":
        file_name = asksaveasfilename(defaultextension=".txt", filetypes=[("Textfile", "*.txt")])
        if not file_name:
            file_name = "/untitled.*"
    if file_name != "/untitled.*":
        file = open(file_name, 'w')
        file.write(assembler_editor.get(1.0, END))
        file.close()

    root.title("CPU Compiler: " + file_name)


# copy from the editor widget
def copy():
    assembler_editor.clipboard_clear()
    assembler_editor.clipboard_append(assembler_editor.selection_get())


# paste into the editor widget
def paste():
    try:
        assembler_editor.insert(INSERT, assembler_editor.clipboard_get())
    except TclError:
        pass


# clear editor widget
def clearall():
    assembler_editor.delete(1.0, END)


# this functions is called whenever the root window is resized, thus rescaling every frame in it
def on_resize(_event):
    width = root.winfo_width()
    h_width = int(width / 2)
    q_width = int(width / 4)
    height = root.winfo_height()

    editor_frame.config(width=h_width, height=height - 30)
    assembler_editor.config(width=h_width, height=height - 30)
    mnemonic_frame.config(width=q_width, height=height - 30)
    mnemonic_editor.config(width=q_width, height=height - 30)
    opcode_frame.config(width=q_width, height=height - 30)
    opcode_editor.config(width=q_width, height=height - 30)
    top_frame.config(width=width, height=30)
    button_frame.config(width=h_width, height=30)
    label1_frame.config(width=q_width, height=30)
    label2_frame.config(width=q_width, height=30)


# inserts a given string into the display frames for mnemonics and opcode
def set_display_frames(mnemonic: str, opcode: str):
    opcode_editor.config(state=NORMAL)
    mnemonic_editor.config(state=NORMAL)

    opcode_editor.delete("1.0", END)
    mnemonic_editor.delete("1.0", END)

    opcode_editor.insert("1.0", opcode)
    mnemonic_editor.insert("1.0", mnemonic)

    opcode_editor.config(state=DISABLED)
    mnemonic_editor.config(state=DISABLED)


# exports the latest successful build
def export_build():
    if successful_build:
        export_name = asksaveasfilename(defaultextension=".txt", filetypes=[("Textfile", "*.txt")])
        if export_name:
            export_file = open(export_name, "w+")
            export_file.write("v2.0 raw\n")
            export_file.write(build_oc)
            export_file.close()
    else:
        showerror("Build failed", "Latest build was not successful, please debug your build!")


# exports the mnemonics from the latest successful build
def export_mnemonics():
    if successful_build:
        export_name = asksaveasfilename(defaultextension=".txt", filetypes=[("Textfile", "*.txt")])
        if export_name:
            export_file = open(export_name, "w+")
            export_file.write(build_mn)
            export_file.close()
    else:
        showerror("Build failed", "Latest build was not successful, please debug your build!")


# displays the building errors on request
def debug_build():
    if successful_build:
        showinfo("Build successful", "The latest build was successful!\nNo Errors returned from the compiler")
    else:
        try:
            compiler.compile_code(assembler_editor.get("1.0", END))
        except (compiler.NonExistingInstructionError, compiler.NumberFormatError, compiler.InvalidSyntax) as e:
            showerror("An Error occurred", e)


# opens the simulation tab with an instance of CPU as the running interpreter. Parses the latest build (if successful) into a list for the interpreter's ram
def simulate_build():

    def kill_simulator():
        simulate_button.config(state=NORMAL)
        simulator.destroy()

    def sim_console_write(_s: str):
        simulator_console.config(state=NORMAL)
        simulator_console.insert(END, _s)
        simulator_console.config(state=DISABLED)

    def cycle(t=None):
        callback = current_interpreter.exec_next()
        sim_console_write(callback)

        if t and t > 0:
            while callback != "Halted Execution":
                sleep(t)
                callback = current_interpreter.exec_next()
                sim_console_write(callback)
                root.update()

    if successful_build:
        simulate_button.config(state=DISABLED)

        # parse build_oc into ram list
        s = StringIO(build_oc)
        ram_content = [0 for _ in range(256)]
        for i in range(255):
            content = s.readline()
            if not content:
                break
            ram_content[i] = int(content, 16)

        # set up running CPU
        current_interpreter = CPU(ram_content)

        # set up simulation window
        simulator = Toplevel(root)
        simulator.protocol("WM_DELETE_WINDOW", kill_simulator)
        simulator.title("CPU Simulator")
        simulator_console = Text(simulator, width=54, height=32)
        simulator_console.config(state=DISABLED)
        simulator_console.pack(side=BOTTOM)
        simulator_frame = Frame(simulator)
        simulator_frame.pack(side=TOP)
        Button(simulator_frame, text="Execute Next Instruction", bg="white", command=cycle, relief=FLAT).pack(side=LEFT)
        interval = StringVar()
        Label(simulator_frame, text="Time between each Instruction:", bg="white").pack(side=LEFT)
        Entry(simulator_frame, bg="white", textvariable=interval, width=7).pack(side=LEFT)
        Button(simulator_frame, text="Step through", bg="white", command=lambda: cycle(float(interval.get())), relief=FLAT).pack(side=LEFT)

    else:
        showerror("Build failed", "Latest build was not successful, please debug your build!")


# some variables and constants
file_name = "/untitled.*"
font = ("Arial", 11)
successful_build = False
build_oc = ""
build_mn = ""

# setting up root widget
root = Tk()
root.geometry("752x500")
root.title("CPU Compiler: " + file_name)

# setting up root title menus
menu = Menu(root)
root.config(menu=menu)
root.pack_propagate(False)

file_menu = Menu(root)
menu.add_cascade(label="File", menu=file_menu)

file_menu.add_command(label="Open", command=opn)
file_menu.add_command(label="Save", command=save)
file_menu.add_command(label="Save As", command=lambda: save(None, True))
file_menu.add_separator()
file_menu.add_command(label="Close", command=kill)

edit_menu = Menu(root)
menu.add_cascade(label="Edit", menu=edit_menu)

edit_menu.add_command(label="Copy", command=copy)
edit_menu.add_command(label="Paste", command=paste)
edit_menu.add_separator()
edit_menu.add_command(label="Clear All", command=clearall)

export_menu = Menu(root)
menu.add_cascade(label="Export", menu=export_menu)

export_menu.add_command(label="Export Mnemonics", command=export_mnemonics)
export_menu.add_command(label="Export Build", command=export_build)

# setting up frames
top_frame = Frame(root)
top_frame.pack(side=TOP)

editor_frame = Frame(root)
editor_frame.pack_propagate(False)
editor_frame.pack(side=LEFT)

opcode_frame = Frame(root, bg="black")
opcode_frame.pack_propagate(False)
opcode_frame.pack(side=RIGHT)

mnemonic_frame = Frame(root, bg="black")
mnemonic_frame.pack_propagate(False)
mnemonic_frame.pack(side=RIGHT)

# setting up opcode_editor display
opcode_editor = Text(opcode_frame, font=font, relief=FLAT)
opcode_editor.pack()

# setting up mnemonic_editor display
mnemonic_editor = Text(mnemonic_frame, font=font, relief=FLAT)
mnemonic_editor.pack(padx=1)

# setting up assembler_editor
assembler_editor = Editor(editor_frame, font=font)
editor_scroll = Scrollbar(editor_frame, command=assembler_editor.yview)
assembler_editor.config(yscrollcommand=editor_scroll.set)
editor_scroll.pack(side=LEFT, fill=Y)
assembler_editor.pack()

# setting up top frame with labels and buttons
button_frame = Frame(top_frame)
button_frame.pack(side=LEFT)
label1_frame = Frame(top_frame)
label1_frame.pack(side=RIGHT)
label2_frame = Frame(top_frame, bg="black")
label2_frame.pack(side=RIGHT)

Label(label1_frame, text="Opcode", font=("Arial", 11, "bold"), bg="white").pack(expand=True, fill=BOTH)
Label(label2_frame, text="Mnemonics", font=("Arial", 11, "bold"), bg="white").pack(expand=True, fill=BOTH, padx=1)
Button(button_frame, text="Debug Build", font=font, command=debug_build, relief=FLAT).pack(side=LEFT, expand=True, fill=BOTH)
simulate_button = Button(button_frame, text="Simulate Build", font=font, command=simulate_build, relief=FLAT)
simulate_button.pack(side=LEFT, expand=True, fill=BOTH)

# starting updater Thread
update_thread = UpdateThread()
update_thread.start()

# bind events
root.protocol("WM_DELETE_WINDOW", kill)
root.bind("<Alt-F4>", kill)
root.bind("<Control-s>", save)
root.bind("<Configure>", on_resize)

root.mainloop()
