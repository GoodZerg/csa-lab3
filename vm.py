import sys

from file_wrapper import *
from control_unit import *
from data_path import *


def main(file, input_f):
    code = rdf(file)
    args = rd_input(input_f)

    for line_i, line in enumerate(code, 0):
        if line["opcode"] == "halt":
            start_of_variables = line_i + 1
            break
    data_path = DP(code, args, start_of_variables)
    control_unit = CU(data_path)

    output, inst_count, tick_count = control_unit.run_machine()

    print(
        f"{''.join(output)}\n\ninstruction_count: {inst_count!s}\ntick: {tick_count!s}"
    )


if __name__ == "__main__":
    if len(sys.argv) != 4:
        exception_noarg("wrong arguments")
    _, code_input, input_file_name, log_name = sys.argv
    logging.getLogger().setLevel(logging.DEBUG)

    formatter = logging.Formatter("[%(levelname)s]  %(message)s")
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(log_name, mode="w", encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)

    main(code_input, input_file_name)
