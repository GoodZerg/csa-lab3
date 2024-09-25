import sys

from lexer import *
from utils import *
from file_wrapper import *


"""TODO JSON_BY_OPCODE"""


def translate_string(name, it):
    massive = [json_by_opcode(it, Opcode.ADDR_ON_TOP.value, variable_names[name])]
    it += 1
    jmp_index = it
    massive.append(json_by_opcode(it, Opcode.PUSH.value, 1))
    it += 1
    massive.append(json_by_opcode_noarg(it, Opcode.SUM.value))
    it += 1
    massive.append(json_by_opcode_noarg(it, Opcode.DUP.value))
    it += 1
    massive.append(json_by_opcode_noarg(it, Opcode.VAR_ON_TOP.value))
    it += 1
    massive.append(json_by_opcode_noarg(it, Opcode.EMIT.value))
    it += 1
    massive.append(json_by_opcode_noarg(it, Opcode.DUP.value))
    it += 1
    massive.append(json_by_opcode(it, Opcode.ADDR_ON_TOP.value, variable_names[name]))
    it += 1
    massive.append(json_by_opcode_noarg(it, Opcode.SWAP.value))
    it += 1
    massive.append(json_by_opcode_noarg(it, Opcode.SUB.value))
    it += 1
    massive.append(json_by_opcode(it, Opcode.ADDR_ON_TOP.value, variable_names[name]))
    it += 1
    massive.append(json_by_opcode_noarg(it, Opcode.VAR_ON_TOP.value))
    it += 1
    massive.append(json_by_opcode_noarg(it, Opcode.SUB.value))
    it += 1
    massive.append(json_by_opcode(it, Opcode.PUSH.value, 0))
    it += 1
    massive.append(json_by_opcode_noarg(it, Opcode.EQ.value))
    it += 1
    massive.append(json_by_opcode(it, Opcode.JZS.value, jmp_index))
    it += 1
    massive.append(json_by_opcode_noarg(it, Opcode.DROP.value))
    it += 1
    return massive, it


def translate(text):
    """
    Translate text to machines code
    """
    strings = []
    terms = parse_terms(text)
    machine_code = []
    jmp_stack = []
    else_flag = False
    count = 0
    for term in terms:
        words = term.symbol.split(" ")
        if words[0] == "if":
            machine_code.append(None)
            jmp_stack.append(count)
        elif words[0] == "else":
            if_index = jmp_stack.pop()
            machine_code[if_index] = json_by_term(
                if_index, Opcode.JZS.value, count + 1, terms[if_index]
            )
            machine_code.append(None)
            jmp_stack.append(count)
            else_flag = True
        elif words[0] == "endif":
            if_index = jmp_stack.pop()
            count -= 1
            if else_flag:
                machine_code[if_index] = json_by_opcode(
                    if_index, Opcode.JMP.value, count + 1
                )
            else:
                machine_code[if_index] = json_by_opcode(
                    if_index, Opcode.JZS.value, count + 1
                )
        elif words[0] == "begin":
            jmp_stack.append(count)
            count -= 1
        elif words[0] == "until":
            jmp_index = jmp_stack.pop()
            machine_code.append(json_by_opcode(count, Opcode.JZS.value, jmp_index))
        elif is_number(words[0]):
            machine_code.append(json_by_term(count, Opcode.PUSH.value, words[0], term))
        elif words[0] in variable_names:
            if len(words) == 5:
                machine_code.append(
                    json_by_term(
                        count,
                        Opcode.ADDR_ON_TOP.value,
                        variable_names[words[1]],
                        Term(term.line, 2, words[1]),
                    )
                )
                count += 1
                machine_code.append(
                    json_by_term_noarg(
                        count, Opcode.VAR_ON_TOP.value, Term(term.line, 3, words[2])
                    )
                )
                count += 1
                machine_code.append(
                    json_by_term(
                        count,
                        Opcode.ADDR_ON_TOP.value,
                        variable_names[words[0]],
                        Term(term.line, 1, words[0]),
                    )
                )
                count += 1
                machine_code.append(
                    json_by_term_noarg(
                        count, Opcode.SUM.value, Term(term.line, 4, words[3])
                    )
                )
                count += 1
                if words[4] == "!":
                    machine_code.append(
                        json_by_term_noarg(
                            count, Opcode.SAVE_VAR, Term(term.line, 5, words[4])
                        )
                    )
                else:
                    machine_code.append(
                        json_by_term_noarg(
                            count, Opcode.VAR_ON_TOP.value, Term(term.line, 5, words[4])
                        )
                    )
            else:
                machine_code.append(
                    json_by_term(
                        count, Opcode.ADDR_ON_TOP.value, variable_names[words[0]], term
                    )
                )
        elif words[0] == '."':
            strings.append(str(" ".join(words)[3:-1]))
            massive, plus_count = translate_string(str(" ".join(words)[3:-1]), count)
            count = plus_count - 1
            for i in massive:
                machine_code.append(i)
        else:
            machine_code.append(json_by_term_noarg(count, word2opcode(words[0]), term))
        count += 1
    for var in vars_count:
        machine_code.append(json_by_arg(count, 0))
        count += 1
    for words in strings:
        words = words.replace("\\n", "\n")
        machine_code.append(json_by_arg(count, len(words)))
        for symbol_line, symbol in enumerate(words, 1):
            machine_code.append(json_by_arg(count + symbol_line, ord(symbol)))
    return machine_code


def main(source, target):
    with open(source, encoding="utf-8") as file:
        source = file.read()

    code = translate(source)

    wrf(target, code)
    variable_names.clear()
    vars_count.clear()
    print("OK.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        exception_noarg("Wrong args")
    _, input_file, output_file = sys.argv
    main(input_file, output_file)
