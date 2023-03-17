# data: int base 10 array
def write_content(data):
    content = "v2.0 raw\n"
    for d in data:
        content += hex(d).replace("0x", "") + " "
    rom = open("rom", "w+")
    rom.write(content)
    rom.close()


write_content([0xff for _ in range(256)])

