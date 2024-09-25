from collections import namedtuple
from enum import Enum


class Opcode(str, Enum):
    SUM = "sum"
    SUB = "sub"
    MUL = "mul"
    DIV = "div"
    MOD = "mod"

    DUP = "dup"
    PUSH = "push"
    DROP = "drop"
    SWAP = "swap"

    NOT_EQ = "not_eq"
    EQ = "eq"
    MORE = "more"
    LESS = "less"

    PRINT = "print"
    EMIT = "emit"
    READ = "read"
    ADDR_ON_TOP = "addr_on_top"
    SAVE_VAR = "save_var"
    VAR_ON_TOP = "var_on_top"

    JZS = "jzs"
    JMP = "jmp"
    HALT = "halt"

    def __str__(self):
        return str(self.value)


class Term(namedtuple("Term", "line word symbol")):
    """Описание символов из текста программы в виде (строка номер_в_строке символ)"""

    pass
