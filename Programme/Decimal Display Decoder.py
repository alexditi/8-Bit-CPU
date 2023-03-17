from rom_writer import write_content

disp_decode = {"0": 0b01110111, "1": 0b01000001, "2": 0b00111011,
               "3": 0b01101011, "4": 0b01001101, "5": 0b01101110,
               "6": 0b01111110, "7": 0b01000011, "8": 0b01111111,
               "9": 0b01101111, " ": 0b00000000}
d = []

for n in range(256):
    n = ("  " + str(n))[::-1]
    d.append(
        (disp_decode.get(n[2]) << 16)
        | (disp_decode.get(n[1]) << 8)
        | (disp_decode.get(n[0]))
    )

write_content(d)

