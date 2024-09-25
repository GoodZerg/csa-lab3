from opcodes import Opcode


def word2opcode(word):
    return {
        "+":    Opcode.SUM.value,
        "-":    Opcode.SUB.value,
        "*":    Opcode.MUL.value,
        "/":    Opcode.DIV.value,
        "mod":  Opcode.MOD.value,
        "dup":  Opcode.DUP.value,
        "drop": Opcode.DROP.value,
        "swap": Opcode.SWAP.value,
        "=":    Opcode.EQ.value,
        ">":    Opcode.MORE.value,
        "<":    Opcode.LESS.value,
        ".":    Opcode.PRINT.value,
        "exit": Opcode.HALT.value,
        "!":    Opcode.SAVE_VAR.value,
        "@":    Opcode.VAR_ON_TOP.value,
        "#":    Opcode.READ.value,
        "emit": Opcode.EMIT.value,
        "!=":   Opcode.NOT_EQ.value,
    }.get(word)


def is_number(word):
    try:
        int(word)
    except ValueError:
        return False
    else:
        return True


def exception_by_lex(text, line, column, word):
    raise Exception("Error in [" + str(line) + ", " + str(column) + ", " + word + " ]:" + text)


def exception_noarg(text):
    raise Exception("Error: " + text)


def json_by_arg(it, arg):
    return {"index": it, "arg": arg}


def json_by_opcode(it, opcode, arg):
    return {"index": it, "opcode": opcode, "arg": arg}


def json_by_opcode_noarg(it, opcode):
    return {"index": it, "opcode": opcode}


def json_by_term(it, opcode, arg, term):
    return {"index": it, "opcode": opcode, "arg": arg, "term": term}


def json_by_term_noarg(it, opcode, term):
    return {"index": it, "opcode": opcode, "term": term}

