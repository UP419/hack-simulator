from __future__ import annotations

import ctypes as ct


class HackSimulator:
    ARG_MAP = {
        "000": "",
        "001": "M=",
        "010": "D=",
        "011": "MD=",
        "100": "A=",
        "101": "AM=",
        "110": "AD=",
        "111": "AMD=",
    }

    COMP_MAP = {
        "0101010": "0",
        "0111111": "1",
        "0111010": "-1",
        "0001100": "D",
        "0110000": "A",
        "1110000": "M",
        "0001101": "!D",
        "0110001": "!A",
        "1110001": "!M",
        "0001111": "-D",
        "0110011": "-A",
        "1110011": "-M",
        "0011111": "D+1",
        "0110111": "A+1",
        "1110111": "M+1",
        "0001110": "D-1",
        "0110010": "A-1",
        "1110010": "M-1",
        "0000010": "D+A",
        "1000010": "D+M",
        "0010011": "D-A",
        "0000111": "A-D",
        "1010011": "D-M",
        "1000111": "M-D",
        "0000000": "D&A",
        "1000000": "D&M",
        "0010101": "D|A",
        "1010101": "D|M",
    }

    register_num = 32768
    file_name = ""
    ram_list = [ct.c_short(0).value] * register_num
    used_ram_list = [False] * register_num
    curr_D = ct.c_short(0).value
    curr_A = ct.c_short(0).value
    curr_line = 0
    lines = [""]
    cycle_num = 0
    res_file = open("file", "w")

    @classmethod
    def load_from(cls, file_name: str, cycles: int) -> HackSimulator:
        cls.file_name = file_name
        cls.cycle_num = cycles
        return cls()

    def execute(self) -> None:
        self.lines.remove("")
        if self.file_name != "" and self.file_name[-4:] == "hack":
            res_file_name = self.file_name[:-4] + "out"
            self.res_file = open(res_file_name, "w")
            self.fill_lines()
            for i in range(self.cycle_num):
                if self.curr_line == len(self.lines) or self.curr_line > len(
                    self.lines
                ):
                    break
                if self.lines[self.curr_line] != "":
                    self.simulate_line(self.lines[self.curr_line])
            self.print_registers()
            self.res_file.close()

    def fill_lines(self) -> None:
        code = open(self.file_name)
        for line in code:
            line = line.partition("//")[0]
            line = line.strip()
            if len(line) > 0:
                self.lines.append(line)
        code.close()

    def simulate_line(self, line: str) -> None:
        if line[0] == "0":
            self.curr_A = ct.c_short(int(line[1:], 2)).value
            self.curr_line += 1
        else:
            comp = line[3:10]
            dest = line[10:13]
            jump = line[13:]
            if jump == "000":
                self.simulate_command(self.ARG_MAP[dest], self.COMP_MAP[comp])
                self.curr_line += 1
            else:
                self.curr_line = self.simulate_jump(jump)

    def print_registers(self) -> None:
        for i in range(self.register_num):
            if self.used_ram_list[i]:
                self.res_file.write(str(self.ram_list[i]) + "\n")
            else:
                self.res_file.write("\n")

    def simulate_command(self, dest: str, comp: str) -> None:
        res = ct.c_short(self.compute(comp)).value
        if dest == "A=":
            self.curr_A = res
        elif dest == "M=":
            self.ram_list[self.curr_A] = res
            self.used_ram_list[self.curr_A] = True
        elif dest == "D=":
            self.curr_D = res
        elif dest == "MD=":
            self.curr_D = res
            self.ram_list[self.curr_A] = res
            self.used_ram_list[self.curr_A] = True
        elif dest == "AM=":
            self.ram_list[self.curr_A] = res
            self.used_ram_list[self.curr_A] = True
            self.curr_A = res
        elif dest == "AD=":
            self.curr_D = res
            self.curr_A = res
        elif dest == "AMD=":
            self.curr_D = res
            self.ram_list[self.curr_A] = res
            self.used_ram_list[self.curr_A] = True
            self.curr_A = res

    def compute(self, comp: str) -> int:
        if comp == "0":
            return 0
        elif comp == "1":
            return 1
        elif comp == "-1":
            return -1
        elif comp == "D":
            return self.curr_D
        elif comp == "A":
            return self.curr_A
        elif comp == "M":
            return self.ram_list[self.curr_A]
        elif comp == "!D":
            return ~self.curr_D
        elif comp == "!A":
            return ~self.curr_A
        elif comp == "!M":
            return ~self.ram_list[self.curr_A]
        elif comp == "-D":
            return -self.curr_D
        elif comp == "-A":
            return -self.curr_A
        elif comp == "-M":
            return -self.ram_list[self.curr_A]
        elif comp == "D+1":
            return self.curr_D + 1
        elif comp == "A+1":
            return self.curr_A + 1
        elif comp == "M+1":
            return self.ram_list[self.curr_A] + 1
        elif comp == "D-1":
            return self.curr_D - 1
        elif comp == "A-1":
            return self.curr_A - 1
        elif comp == "M-1":
            return self.ram_list[self.curr_A] - 1
        elif comp == "D+A":
            return self.curr_A + self.curr_D
        elif comp == "D+M":
            return self.curr_D + self.ram_list[self.curr_A]
        elif comp == "D-A":
            return self.curr_D - self.curr_A
        elif comp == "A-D":
            return self.curr_A - self.curr_D
        elif comp == "D-M":
            return self.curr_D - self.ram_list[self.curr_A]
        elif comp == "M-D":
            return self.ram_list[self.curr_A] - self.curr_D
        elif comp == "D&A":
            return self.curr_D & self.curr_A
        elif comp == "D&M":
            return self.curr_D & self.ram_list[self.curr_A]
        elif comp == "D|A":
            return self.curr_D | self.curr_A
        elif comp == "D|M":
            return self.curr_D | self.ram_list[self.curr_A]
        return 0

    def simulate_jump(self, jump: str) -> int:
        if jump == "111":
            return self.curr_A
        if jump == "001" and self.curr_D > 0:
            return self.curr_A
        if jump == "010" and self.curr_D == 0:
            return self.curr_A
        if jump == "011" and (self.curr_D > 0 or self.curr_D == 0):
            return self.curr_A
        if jump == "100" and self.curr_D < 0:
            return self.curr_A
        if jump == "101" and self.curr_D != 0:
            return self.curr_A
        if jump == "110" and (self.curr_D < 0 or self.curr_D == 0):
            return self.curr_A
        return self.curr_line + 1
