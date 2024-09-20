from config import *


ALU_COMMANDS = [
    # SUM - 0
    lambda x, y: x + y,
    # SUB - 1
    lambda x, y: x - y,
    # MUL - 2
    lambda x, y: x * y,
    # DIV - 3
    lambda x, y: x // y,
    # MOD - 4
    lambda x, y: x % y,
    # NOT EQ - 5
    lambda x, y: 1 if x != y else 0,
    # EQ - 6
    lambda x, y: 1 if x == y else 0,
    # MORE - 7
    lambda x, y: 1 if x < y else 0,
    # LESS - 8
    lambda x, y: 1 if x > y else 0,
]


class ALU:
    n_flag = None
    z_flag = None
    v_flag = None
    value = None
    first_value = None
    second_value = None

    def __init__(self):
        self.n_flag = 0
        self.z_flag = 0
        self.v_flag = 0
        self.value = 0
        self.first_value = 0
        self.second_value = 0

    def do_operation(self, command):
        alu = ALU_COMMANDS[command]
        result = alu(self.first_value, self.second_value)
        result = self.set_flags(result)
        self.value = result

    def set_flags(self, result):
        self.n_flag = 0
        self.z_flag = 0
        self.v_flag = 0

        if result < 0:
            self.n_flag = 1

        if result == 0:
            self.z_flag = 1

        if result < MIN_NUMBER:
            result %= abs(MIN_NUMBER)
            self.v_flag = 1
        elif result > MAX_NUMBER:
            result %= MAX_NUMBER
            self.v_flag = 1

        return result
