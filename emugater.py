def nand(a, b):
    return int(not (a and b))

def neg(a):
    return nand(a, a)

def aand(a, b):
    return neg(nand(a, b))

def oor(a, b):
    return nand(neg(a), neg(b))

def decode_bits(bits):
    if len(bits) == 1:
        return [neg(bits[0]), bits[0]]
    
    head, *tail = bits
    neg_head = neg(head)

    upper = decode_bits(tail)
    lower = decode_bits(tail)

    return [aand(neg_head, x) for x in upper] + [aand(head, x) for x in lower]

class Register:
    def __init__(self, bits=8):
        self.bits = bits

        self.data = [0] * self.bits
        self.set = [0] * self.bits
        self.enable = [0] * self.bits
    
    def simulate(self, inp):
        assert len(inp) == self.bits

        output = [0] * self.bits

        for i, d in enumerate(inp):
            q = self.data[i]
            s = self.set[i]
            e = self.enable[i]

            keep = aand(neg(s), q)
            write = aand(s, d)

            self.data[i] = oor(keep, write)
            output[i] = aand(self.data[i], e)

        return output
    
    def __str__(self) -> str:
        return f"Register Data: {self.data}"
    
    def __repr__(self) -> str:
        return self.__str__()

class Ram:
    def __init__(self, bytes=1):
        self.addrsize = bytes*8
        self.registers = [Register() for _ in range(2 ** (bytes*8))]

    def multiplex(self, active, simulated, output):
        a = aand(active, simulated)
        b = aand(neg(active), output)

        return oor(a, b)
    
    # 'A' register defines address; bus carries the i/o
    def simulate(self, bset, benable, ar_bits, bus_bits):
        assert len(bus_bits) == self.addrsize and len(ar_bits) == self.addrsize

        decs = decode_bits(ar_bits)
        output = [0] * self.addrsize

        for i, register in enumerate(self.registers):
            active = decs[i]
            register.set = [aand(active, bset)] * self.addrsize
            register.enable = [aand(active, benable)] * self.addrsize

            simulated = register.simulate(bus_bits)
            output = [self.multiplex(active, simulated[i], output[i]) for i in range(0, len(simulated))]

        return output

bus = [0] * 8

char_mapper = {
    'H': [0, 1, 0, 0,   1, 0, 0, 0],
    'd': [],
    'e': [0, 1, 1, 0,   0, 1, 0, 1],
    'l': [],
    'o': [],
    'r': [],
    'w': [],
    ' ': [],
}

def byte_string(s: str):
    output = [([0] * 8) for i in range(0, len(s))]

    for i in range(0, len(s)):
        output[i] = char_mapper[s[i]]

    return output

def print_byte_string(s):
    pass

def bits_to_int(bits):
    return int("".join(str(b) for b in bits), 2)

def bits_to_char(bits):
    return chr(bits_to_int(bits))

ar = Register() # 'A' register
ram = Ram(bytes=1)

print("Emulation start")

# Modify RAM contents
def write_ram(address, content):
    ar.set = [1] * len(ar.set)
    ar.enable = [0] * len(ar.enable)
    ar.simulate(address)
    print(f"RAM Address: {address}")

    bus = content

    ram_output = ram.simulate(bset=1, benable=1, ar_bits=ar.data, bus_bits=bus)
    print(f"RAM Output: {ram_output}")

def read_ram(address):
    ar.set = [1] * len(ar.set)
    ar.enable = [0] * len(ar.enable)
    ar.simulate(address)

    return ram.simulate(bset=0, benable=1, ar_bits=ar.data, bus_bits=bus)

write_ram([0, 0, 0, 0, 0, 0, 0, 0], char_mapper['H'])
write_ram([0, 0, 0, 0, 0, 0, 0, 1], char_mapper['e'])

read_char = read_ram([0, 0, 0, 0, 0, 0, 0, 1])
print(f"RAM Content: {read_char}")

# Strings
s = byte_string("Hello world")

print_loc = [0, 0, 1, 0, 1, 1, 1, 0]
