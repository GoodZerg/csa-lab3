import json
from opcodes import *


def wrf(filename, code):
    with open(filename, "w", encoding="utf-8") as file:
        buffer = []
        for instruction in code:
            buffer.append(json.dumps(instruction, indent=4))
        file.write("[" + ",\n".join(buffer) + "]")


def rdf(filename):
    with open(filename, encoding="utf-8") as file:
        code = json.loads(file.read())
    for instruction in code:
        if "opcode" in instruction:
            instruction["opcode"] = Opcode(instruction["opcode"])

        if "term" in instruction:
            instruction["term"] = Term(
                instruction["term"][0], instruction["term"][1], instruction["term"][2]
            )
    return code


def rd_input(filename):
    with open(filename, encoding="utf-8") as file:
        raw = file.read().strip()
        input_token = []
        for char in raw:
            input_token.append(char)
    return input_token
