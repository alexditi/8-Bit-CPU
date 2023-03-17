from rom_writer import write_content

d = [0 for _ in range(2**14)]

# Control Signal overview
LF = 0b10000000000000000000000
CC = 0b01000000000000000000000
RR = 0b00100000000000000000000
WR = 0b00010000000000000000000
LM = 0b00001000000000000000000
LI = 0b00000100000000000000000
IP = 0b00000010000000000000000
EP = 0b00000001000000000000000
LP = 0b00000000100000000000000
LO = 0b00000000010000000000000
O4 = 0b00000000001000000000000
O3 = 0b00000000000100000000000
O2 = 0b00000000000010000000000
O1 = 0b00000000000001000000000
ET = 0b00000000000000100000000
LT = 0b00000000000000010000000
EA = 0b00000000000000001000000
LA = 0b00000000000000000100000
EB = 0b00000000000000000010000
LB = 0b00000000000000000001000
EC = 0b00000000000000000000100
LC = 0b00000000000000000000010
HLT = 0b00000000000000000000001

# ALU Operations
ADD = O1
SUB = O2
AND = O1 | O2
OR = O3
NOT = O3 | O1
XOR = O3 | O2
DEC = O1 | O2 | O3
INC = O4
AOUT = O1 | O4


# Flag Signal Overview
CF = 0b100      # carry flag
ZF = 0b010      # zero flag
NF = 0b001      # negative flag

# fetch cycle
for i in range(2048):
    d[i << 3 | 0b000] = EP | LM
    d[i << 3 | 0b001] = RR | LI | LT | IP

# instruction programmer
for FR_state in range(8):
    # non-conditional instructions

    # NOOP: idle CPU for the next 8 cycles
    # output 0 as control word, but the control rom is already zeroed at all addresses

    # LVA: A = P
    inst = 0b00000001
    d[FR_state << 11 | (inst << 3) + 2] = EP | LM
    d[FR_state << 11 | (inst << 3) + 3] = IP | RR | LA
    d[FR_state << 11 | (inst << 3) + 4] = CC

    # LMA: A = RAM(P)
    inst = 0b00000010
    d[FR_state << 11 | (inst << 3) + 2] = EP | LM
    d[FR_state << 11 | (inst << 3) + 3] = IP | RR | LM
    d[FR_state << 11 | (inst << 3) + 4] = RR | LA
    d[FR_state << 11 | (inst << 3) + 5] = CC

    # LVB: B = P
    inst = 0b00000011
    d[FR_state << 11 | (inst << 3) + 2] = EP | LM
    d[FR_state << 11 | (inst << 3) + 3] = IP | RR | LB
    d[FR_state << 11 | (inst << 3) + 4] = CC

    # LMB: B = RAM(P)
    inst = 0b00000100
    d[FR_state << 11 | (inst << 3) + 2] = EP | LM
    d[FR_state << 11 | (inst << 3) + 3] = IP | RR | LM
    d[FR_state << 11 | (inst << 3) + 4] = RR | LB
    d[FR_state << 11 | (inst << 3) + 5] = CC

    # LVC: C = P
    inst = 0b00000101
    d[FR_state << 11 | (inst << 3) + 2] = EP | LM
    d[FR_state << 11 | (inst << 3) + 3] = IP | RR | LC
    d[FR_state << 11 | (inst << 3) + 4] = CC

    # LMC: C = RAM(P)
    inst = 0b00000110
    d[FR_state << 11 | (inst << 3) + 2] = EP | LM
    d[FR_state << 11 | (inst << 3) + 3] = IP | RR | LM
    d[FR_state << 11 | (inst << 3) + 4] = RR | LC
    d[FR_state << 11 | (inst << 3) + 5] = CC

    # ADD: A = A + P
    inst = 0b00000111
    d[FR_state << 11 | (inst << 3) + 2] = EP | LM
    d[FR_state << 11 | (inst << 3) + 3] = IP | RR | LT
    d[FR_state << 11 | (inst << 3) + 4] = ADD | LA | LF
    d[FR_state << 11 | (inst << 3) + 5] = CC

    # ADDB: A = A + B
    inst = 0b00001000
    d[FR_state << 11 | (inst << 3) + 2] = EB | LT
    d[FR_state << 11 | (inst << 3) + 3] = ADD | LA | LF
    d[FR_state << 11 | (inst << 3) + 4] = CC

    # ADDC: A = A + C
    inst = 0b00001001
    d[FR_state << 11 | (inst << 3) + 2] = EC | LT
    d[FR_state << 11 | (inst << 3) + 3] = ADD | LA | LF
    d[FR_state << 11 | (inst << 3) + 4] = CC

    # SUB: A = A - P
    inst = 0b00001010
    d[FR_state << 11 | (inst << 3) + 2] = EP | LM
    d[FR_state << 11 | (inst << 3) + 3] = IP | RR | LT
    d[FR_state << 11 | (inst << 3) + 4] = SUB | LA | LF
    d[FR_state << 11 | (inst << 3) + 5] = CC

    # SUBB: A = A - B
    inst = 0b00001011
    d[FR_state << 11 | (inst << 3) + 2] = EB | LT
    d[FR_state << 11 | (inst << 3) + 3] = SUB | LA | LF
    d[FR_state << 11 | (inst << 3) + 4] = CC

    # SUBC: A = A + C
    inst = 0b00001100
    d[FR_state << 11 | (inst << 3) + 2] = EC | LT
    d[FR_state << 11 | (inst << 3) + 3] = SUB | LA | LF
    d[FR_state << 11 | (inst << 3) + 4] = CC

    # AND: A = A - P
    inst = 0b00001101
    d[FR_state << 11 | (inst << 3) + 2] = EP | LM
    d[FR_state << 11 | (inst << 3) + 3] = IP | RR | LT
    d[FR_state << 11 | (inst << 3) + 4] = AND | LA | LF
    d[FR_state << 11 | (inst << 3) + 5] = CC

    # ANDB: A = A - B
    inst = 0b00001110
    d[FR_state << 11 | (inst << 3) + 2] = EB | LT
    d[FR_state << 11 | (inst << 3) + 3] = AND | LA | LF
    d[FR_state << 11 | (inst << 3) + 4] = CC

    # ANDC: A = A + C
    inst = 0b00001111
    d[FR_state << 11 | (inst << 3) + 2] = EC | LT
    d[FR_state << 11 | (inst << 3) + 3] = AND | LA | LF
    d[FR_state << 11 | (inst << 3) + 4] = CC

    # OR: A = A - P
    inst = 0b00010000
    d[FR_state << 11 | (inst << 3) + 2] = EP | LM
    d[FR_state << 11 | (inst << 3) + 3] = IP | RR | LT
    d[FR_state << 11 | (inst << 3) + 4] = OR | LA | LF
    d[FR_state << 11 | (inst << 3) + 5] = CC

    # ORB: A = A - B
    inst = 0b00010001
    d[FR_state << 11 | (inst << 3) + 2] = EB | LT
    d[FR_state << 11 | (inst << 3) + 3] = OR | LA | LF
    d[FR_state << 11 | (inst << 3) + 4] = CC

    # ORC: A = A + C
    inst = 0b00010010
    d[FR_state << 11 | (inst << 3) + 2] = EC | LT
    d[FR_state << 11 | (inst << 3) + 3] = OR | LA | LF
    d[FR_state << 11 | (inst << 3) + 4] = CC

    # XOR: A = A - P
    inst = 0b00010011
    d[FR_state << 11 | (inst << 3) + 2] = EP | LM
    d[FR_state << 11 | (inst << 3) + 3] = IP | RR | LT
    d[FR_state << 11 | (inst << 3) + 4] = XOR | LA | LF
    d[FR_state << 11 | (inst << 3) + 5] = CC

    # XORB: A = A - B
    inst = 0b00010100
    d[FR_state << 11 | (inst << 3) + 2] = EB | LT
    d[FR_state << 11 | (inst << 3) + 3] = XOR | LA | LF
    d[FR_state << 11 | (inst << 3) + 4] = CC

    # XORC: A = A + C
    inst = 0b00010101
    d[FR_state << 11 | (inst << 3) + 2] = EC | LT
    d[FR_state << 11 | (inst << 3) + 3] = XOR | LA | LF
    d[FR_state << 11 | (inst << 3) + 4] = CC

    # NOT: A = NOT P
    inst = 0b00010110
    d[FR_state << 11 | (inst << 3) + 2] = EP | LM
    d[FR_state << 11 | (inst << 3) + 3] = IP | RR | LA
    d[FR_state << 11 | (inst << 3) + 4] = NOT | LA | LF
    d[FR_state << 11 | (inst << 3) + 5] = CC

    # NOTA: A = NOT A
    inst = 0b00010111
    d[FR_state << 11 | (inst << 3) + 2] = NOT | LA | LF
    d[FR_state << 11 | (inst << 3) + 3] = CC

    # NOTB: A = NOT B
    inst = 0b00011000
    d[FR_state << 11 | (inst << 3) + 2] = EB | LA
    d[FR_state << 11 | (inst << 3) + 3] = NOT | LA | LF
    d[FR_state << 11 | (inst << 3) + 4] = CC

    # NOTC: A = NOT C
    inst = 0b00011001
    d[FR_state << 11 | (inst << 3) + 2] = EC | LA
    d[FR_state << 11 | (inst << 3) + 3] = NOT | LA | LF
    d[FR_state << 11 | (inst << 3) + 4] = CC

    # DEC AD: A = RAM(P) - 1
    inst = 0b00011010
    d[FR_state << 11 | (inst << 3) + 2] = EP | LM
    d[FR_state << 11 | (inst << 3) + 3] = IP | RR | LM
    d[FR_state << 11 | (inst << 3) + 4] = RR | LA
    d[FR_state << 11 | (inst << 3) + 5] = DEC | LA | LF
    d[FR_state << 11 | (inst << 3) + 6] = CC

    # DEC: A = P - 1
    inst = 0b00011011
    d[FR_state << 11 | (inst << 3) + 2] = EP | LM
    d[FR_state << 11 | (inst << 3) + 3] = IP | RR | LA
    d[FR_state << 11 | (inst << 3) + 4] = DEC | LA | LF
    d[FR_state << 11 | (inst << 3) + 5] = CC

    # DECA: A = A - 1
    inst = 0b00011100
    d[FR_state << 11 | (inst << 3) + 2] = DEC | LA | LF
    d[FR_state << 11 | (inst << 3) + 3] = CC

    # DECB: A = B - 1
    inst = 0b00011101
    d[FR_state << 11 | (inst << 3) + 2] = EB | LA
    d[FR_state << 11 | (inst << 3) + 3] = DEC | LA | LF
    d[FR_state << 11 | (inst << 3) + 4] = CC

    # DECC: A = C - 1
    inst = 0b00011110
    d[FR_state << 11 | (inst << 3) + 2] = EC | LA
    d[FR_state << 11 | (inst << 3) + 3] = DEC | LA | LF
    d[FR_state << 11 | (inst << 3) + 4] = CC

    # INC AD: A = RAM(P) + 1
    inst = 0b00011111
    d[FR_state << 11 | (inst << 3) + 2] = EP | LM
    d[FR_state << 11 | (inst << 3) + 3] = IP | RR | LM
    d[FR_state << 11 | (inst << 3) + 4] = RR | LA
    d[FR_state << 11 | (inst << 3) + 5] = INC | LA | LF
    d[FR_state << 11 | (inst << 3) + 6] = CC

    # INC: A = P + 1
    inst = 0b00100000
    d[FR_state << 11 | (inst << 3) + 2] = EP | LM
    d[FR_state << 11 | (inst << 3) + 3] = IP | RR | LA
    d[FR_state << 11 | (inst << 3) + 4] = INC | LA | LF
    d[FR_state << 11 | (inst << 3) + 5] = CC

    # INCA: A = A + 1
    inst = 0b00100001
    d[FR_state << 11 | (inst << 3) + 2] = INC | LA | LF
    d[FR_state << 11 | (inst << 3) + 3] = CC

    # INCB: A = B + 1
    inst = 0b00100010
    d[FR_state << 11 | (inst << 3) + 2] = EB | LA
    d[FR_state << 11 | (inst << 3) + 3] = INC | LA | LF
    d[FR_state << 11 | (inst << 3) + 4] = CC

    # INCC: A = C + 1
    inst = 0b00100011
    d[FR_state << 11 | (inst << 3) + 2] = EC | LA
    d[FR_state << 11 | (inst << 3) + 3] = INC | LA | LF
    d[FR_state << 11 | (inst << 3) + 4] = CC

    # AOUT: set flags for the A-registers content
    inst = 0b00100100
    d[FR_state << 11 | (inst << 3) + 2] = AOUT | LF
    d[FR_state << 11 | (inst << 3) + 3] = CC

    # OUTA: Output the A registers content to the output register
    inst = 0b00100101
    d[FR_state << 11 | (inst << 3) + 2] = EA | LO
    d[FR_state << 11 | (inst << 3) + 3] = CC

    # OUTB: Output the B registers content to the output register
    inst = 0b00100110
    d[FR_state << 11 | (inst << 3) + 2] = EB | LO
    d[FR_state << 11 | (inst << 3) + 3] = CC

    # OUTC: Output the C registers content to the output register
    inst = 0b00100111
    d[FR_state << 11 | (inst << 3) + 2] = EC | LO
    d[FR_state << 11 | (inst << 3) + 3] = CC

    # STA: Stores the content of the A register in the given ram address
    inst = 0b00101000
    d[FR_state << 11 | (inst << 3) + 2] = EP | LM
    d[FR_state << 11 | (inst << 3) + 3] = IP | RR | LM
    d[FR_state << 11 | (inst << 3) + 4] = EA | WR
    d[FR_state << 11 | (inst << 3) + 5] = CC

    # STB: Stores the content of the B register in the given ram address
    inst = 0b00101001
    d[FR_state << 11 | (inst << 3) + 2] = EP | LM
    d[FR_state << 11 | (inst << 3) + 3] = IP | RR | LM
    d[FR_state << 11 | (inst << 3) + 4] = EB | WR
    d[FR_state << 11 | (inst << 3) + 5] = CC

    # STC: Stores the content of the C register in the given ram address
    inst = 0b00101010
    d[FR_state << 11 | (inst << 3) + 2] = EP | LM
    d[FR_state << 11 | (inst << 3) + 3] = IP | RR | LM
    d[FR_state << 11 | (inst << 3) + 4] = EC | WR
    d[FR_state << 11 | (inst << 3) + 5] = CC

    # A2B: B = A
    inst = 0b00101011
    d[FR_state << 11 | (inst << 3) + 2] = EA | LB
    d[FR_state << 11 | (inst << 3) + 3] = CC

    # A2C: C = A
    inst = 0b00101100
    d[FR_state << 11 | (inst << 3) + 2] = EA | LC
    d[FR_state << 11 | (inst << 3) + 3] = CC

    # B2A: A = B
    inst = 0b00101101
    d[FR_state << 11 | (inst << 3) + 2] = EB | LA
    d[FR_state << 11 | (inst << 3) + 3] = CC

    # B2C: C = B
    inst = 0b00101110
    d[FR_state << 11 | (inst << 3) + 2] = EB | LC
    d[FR_state << 11 | (inst << 3) + 3] = CC

    # C2A: A = C
    inst = 0b00101111
    d[FR_state << 11 | (inst << 3) + 2] = EC | LA
    d[FR_state << 11 | (inst << 3) + 3] = CC

    # C2B: B = C
    inst = 0b00110000
    d[FR_state << 11 | (inst << 3) + 2] = EC | LB
    d[FR_state << 11 | (inst << 3) + 3] = CC

    # CMP: sets the flags for A - P
    inst = 0b00110001
    d[FR_state << 11 | (inst << 3) + 2] = EP | LM
    d[FR_state << 11 | (inst << 3) + 3] = IP | RR | LT
    d[FR_state << 11 | (inst << 3) + 4] = SUB | LF
    d[FR_state << 11 | (inst << 3) + 5] = CC

    # CMPB: sets the flags for A - B
    inst = 0b00110010
    d[FR_state << 11 | (inst << 3) + 2] = EB | LT
    d[FR_state << 11 | (inst << 3) + 3] = SUB | LF
    d[FR_state << 11 | (inst << 3) + 4] = CC

    # CMPC: sets the flags for A - C
    inst = 0b00110011
    d[FR_state << 11 | (inst << 3) + 2] = EC | LT
    d[FR_state << 11 | (inst << 3) + 3] = SUB | LF
    d[FR_state << 11 | (inst << 3) + 4] = CC

    # JMP: jumps to the given memory address for the next instruction cycle
    inst = 0b00110100
    d[FR_state << 11 | (inst << 3) + 2] = EP | LM
    d[FR_state << 11 | (inst << 3) + 3] = RR | LP
    d[FR_state << 11 | (inst << 3) + 4] = CC

    # RET: returns from the subroutine, going back to the address stored in 0xff
    inst = 0b11111110
    d[FR_state << 11 | (inst << 3) + 2] = ET | LA
    d[FR_state << 11 | (inst << 3) + 3] = INC | LM
    d[FR_state << 11 | (inst << 3) + 4] = RR | LP
    d[FR_state << 11 | (inst << 3) + 5] = CC

    # CALL: jumps to subroutine starting at P, stores the current pointer value in 0xff
    inst = 0b11111111
    d[FR_state << 11 | (inst << 3) + 2] = EP | LM
    d[FR_state << 11 | (inst << 3) + 3] = IP | RR | LA
    d[FR_state << 11 | (inst << 3) + 4] = ET | LM
    d[FR_state << 11 | (inst << 3) + 5] = EP | WR
    d[FR_state << 11 | (inst << 3) + 6] = EA | LP
    d[FR_state << 11 | (inst << 3) + 7] = CC

    # HLT: halts the CPU clock cycle
    inst = 0b00111000
    d[FR_state << 11 | (inst << 3) + 2] = HLT

    # LMAC: A = RAM(C)
    inst = 0b00111001
    d[FR_state << 11 | (inst << 3) + 2] = EC | LM
    d[FR_state << 11 | (inst << 3) + 3] = RR | LA
    d[FR_state << 11 | (inst << 3) + 4] = CC

    # LMBC: B = RAM(C)
    inst = 0b00111010
    d[FR_state << 11 | (inst << 3) + 2] = EC | LM
    d[FR_state << 11 | (inst << 3) + 3] = RR | LB
    d[FR_state << 11 | (inst << 3) + 4] = CC

    # LMCC: C = RAM(C)
    inst = 0b00111011
    d[FR_state << 11 | (inst << 3) + 2] = EC | LM
    d[FR_state << 11 | (inst << 3) + 3] = RR | LC
    d[FR_state << 11 | (inst << 3) + 4] = CC

    # STAC: RAM(C) = A
    inst = 0b00111100
    d[FR_state << 11 | (inst << 3) + 2] = EC | LM
    d[FR_state << 11 | (inst << 3) + 3] = EA | WR
    d[FR_state << 11 | (inst << 3) + 4] = CC

    # STBC: RAM(C) = B
    inst = 0b00111101
    d[FR_state << 11 | (inst << 3) + 2] = EC | LM
    d[FR_state << 11 | (inst << 3) + 3] = EB | WR
    d[FR_state << 11 | (inst << 3) + 4] = CC

    # STCC: RAM(C) = C
    inst = 0b00111110
    d[FR_state << 11 | (inst << 3) + 2] = EC | LM
    d[FR_state << 11 | (inst << 3) + 3] = EC | WR
    d[FR_state << 11 | (inst << 3) + 4] = CC

    # conditional instructions

    # JC: Jumps to the given memory address if the carry bit is set
    inst = 0b00110101
    if FR_state & CF == CF:
        d[FR_state << 11 | (inst << 3) + 2] = EP | LM
        d[FR_state << 11 | (inst << 3) + 3] = RR | LP
        d[FR_state << 11 | (inst << 3) + 4] = CC
    else:
        d[FR_state << 11 | (inst << 3) + 2] = IP
        d[FR_state << 11 | (inst << 3) + 3] = CC

    # JZ: Jumps to the given memory address if the is zero bit is set
    inst = 0b00110110
    if FR_state & ZF == ZF:
        d[FR_state << 11 | (inst << 3) + 2] = EP | LM
        d[FR_state << 11 | (inst << 3) + 3] = RR | LP
        d[FR_state << 11 | (inst << 3) + 4] = CC
    else:
        d[FR_state << 11 | (inst << 3) + 2] = IP
        d[FR_state << 11 | (inst << 3) + 3] = CC

    # JN: Jumps to the given memory address if the is negative bit is set
    inst = 0b00110111
    if FR_state & NF == NF:
        d[FR_state << 11 | (inst << 3) + 2] = EP | LM
        d[FR_state << 11 | (inst << 3) + 3] = RR | LP
        d[FR_state << 11 | (inst << 3) + 4] = CC
    else:
        d[FR_state << 11 | (inst << 3) + 2] = IP
        d[FR_state << 11 | (inst << 3) + 3] = CC

write_content(d)
