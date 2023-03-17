from io import StringIO


class NonExistingInstructionError(Exception):

    def __init__(self, inst):
        super().__init__(f"Error in decoding the current instruction: Cannot find instruction: {inst}")


class NumberFormatError(Exception):

    def __init__(self, number):
        super().__init__(f"Error parsing the following number to hexadecimal: {number}")


class InvalidSyntax(Exception):

    def __init__(self, syntax_error):
        super().__init__(f"Syntax Error: {syntax_error}")


inst_list = ["NOOP", "LVA", "LMA", "LVB", "LMB", "LVC", "LMC", "ADD", "ADDB", "ADDC", "SUB", "SUBB", "SUBC", "AND",
             "ANDB", "ANDC", "OR", "ORB", "ORC", "XOR", "XORB", "XORC", "NOT", "NOTA", "NOTB", "NOTC", "DECAD", "DEC",
             "DECA", "DECB", "DECC", "INCAD", "INC", "INCA", "INCB", "INCC", "AOUT", "OUTA", "OUTB", "OUTC", "STA",
             "STB", "STC", "A2B", "A2C", "B2A", "B2C", "C2A", "C2B", "CMP", "CMPB", "CMPC", "JMP", "JC", "JZ", "JN",
             "HLT", "LMAC", "LMBC", "LMCC", "STAC", "STBC", "STCC", "RET", "CALL"]
inst_dict = {inst_list[i]: hex(i).replace("0x", "0") if i < 16 else hex(i).replace("0x", "") for i in range(len(inst_list))}
inst_dict.update({"RET": "fe", "CALL": "ff"})


def compile_code(code):

    def get_hex(_value):
        try:
            _symbol = _value[:2]
            if _symbol == "0x":
                int_val = int(_value, 16)
            elif _symbol == "0b":
                int_val = int(_value[2:], 2)
            elif _symbol == "0o":
                int_val = int(_value[2:], 8)
            else:
                int_val = int(_value)
        except ValueError:
            raise NumberFormatError(_value)
        if int_val < 16:
            return hex(int_val).replace("0x", "0x0")
        else:
            return hex(int_val)

    # parse mnemonics

    # 1. Strip off comments
    code = StringIO(code)
    op_code = ""
    inst = ""
    line = code.readline()
    while line:
        line = line.replace("\n", "")
        for c in line:
            inst += c
            symbol = inst[len(inst) - 2:]
            if symbol in ["  ", " /", "//"]:
                inst = inst[:len(inst) - 2]
                break
        if inst:
            op_code += inst + "\n"
            inst = ""
        line = code.readline()

    # 2. parse variables and arguments
    code.close()
    code = StringIO(op_code)
    op_code = ""
    variables = {}
    while True:
        line = code.readline().replace("\n", "")
        if not line:
            break

        # variable parser
        if line.find("=") != -1:
            name = ""
            value = ""
            for c in line:
                if c != " " and c != "=":
                    name += c
                else:
                    value = line[line.find("=") + 1:].replace(" ", "")
                    break
            variables.update({name: get_hex(value)})
        # real opcode_editor line without any argument given or label
        elif line in inst_list or line[0] == "#":
            op_code += line + "\n"
        # opcode_editor with argument or single number
        else:
            inst = ""
            for c in line:
                inst += c
                # inst with argument
                if c == " ":
                    inst = inst.replace(" ", "")
                    if inst in inst_list:
                        op_code += inst
                        argument = line[line.find(" ") + 1:]
                        if variables.get(argument):
                            op_code += "\n" + variables.get(argument) + "\n"
                        elif argument[0] == "#":
                            op_code += " " + argument + "\n"
                        else:
                            op_code += "\n" + get_hex(argument) + "\n"
                    else:
                        raise NonExistingInstructionError(inst)
                    break
                # single number
                elif len(inst) == len(line):
                    op_code += get_hex(inst) + "\n"
                    break

    # 3. parse labels
    code.close()
    code = StringIO(op_code)
    op_code = ""
    while True:
        line = code.readline().replace("\n", "")
        if not line:
            break
        if line.find("#") != -1 and line.find(" ") != -1:
            # label as argument
            op_code += f"{line[:line.find(' ')]}\n{line[line.find(' ') + 1:]}\n"
        elif line.find("#") == 0:
            # label defined
            op_code += f"{line} {code.readline()}"
        else:
            op_code += line + "\n"

    code.close()
    code = StringIO(op_code)
    op_code = ""
    label_resolve = {}
    i = 0
    while True:
        line = code.readline().replace("\n", "")
        if not line:
            break
        if line.find("#") != -1 and line.find(" ") != -1:
            label = line[:line.find(" ")]
            label_resolve.update({label: i})
            op_code += line.replace(label + " ", "") + "\n"
        else:
            op_code += line + "\n"

        i += 1

    code.close()
    code = StringIO(op_code)
    op_code = ""
    while True:
        line = code.readline().replace("\n", "")
        if not line:
            break
        if line.find("#") == 0:
            op_code += get_hex(str(label_resolve.get(line))) + "\n"
        else:
            op_code += line + "\n"

    # compile mnemonics to hex code / opcode_editor
    compiled = ""
    inst = ""
    for c in op_code + "\n":
        inst += c
        # instruction or argument
        if c == "\n":
            inst = inst.replace("\n", "")
            if inst in inst_list:
                compiled += inst_dict.get(inst) + "\n"
            elif inst.find("0x") != -1:
                compiled += inst.replace("0x", "") + "\n"
            elif not inst:
                pass
            else:
                raise NonExistingInstructionError(inst)
            inst = ""

    return op_code, compiled


if __name__ == "__main__":
    from sys import argv
    import os
    try:
        if len(argv) >= 2:
            file = open(os.path.realpath(__file__).replace("\\compiler.py", "") + f"\\{argv[1]}", "r")
            file_out = open(os.path.realpath(__file__).replace("\\compiler.py", "") + f"\\{argv[1].replace('.', ' Compiled.')}", "w+")
            file_out.write("v2.0 raw\n")
            mnemonics, opcode = compile_code(file.read())
            file_out.write(opcode)
            file.close()
            file_out.close()
        else:
            raise FileNotFoundError("Missing file path!")
    except (FileNotFoundError, NonExistingInstructionError, NumberFormatError, InvalidSyntax) as e:
        print(e)
        exit(1)
