import logging
from typing import ClassVar

from alu import ALU
from config import *
from signals import *
from stack import Stack


class Memory:
    memory = None
    start_of_variables = None
    value = None

    def __init__(self, code, start_of_variables):
        self.start_of_variables = start_of_variables
        self.memory = [0] * (len(code) + 1)
        self.value = 0
        self.memory[0] = start_of_variables
        for number, instruction in enumerate(code, 1):
            self.memory[number] = instruction

    def read(self, adr):
        self.value = self.memory[adr]

    def write(self, adr):
        self.memory[adr] = self.value


class DP:
    data_stack = None
    top_of_stack = None
    alu = None
    instruction_register = None
    buffer_register = None
    address_register = None
    memory = None
    pc = None
    input_buffer = None
    output_buffer = None

    ar_l: ClassVar[dict] = {}
    mem_s: ClassVar[dict] = {}
    ir_l: ClassVar[dict] = {}
    alu_v: ClassVar[dict] = {}
    alu_l: ClassVar[dict] = {}
    tos_l: ClassVar[dict] = {}
    pc_l: ClassVar[dict] = {}
    ds_l: ClassVar[dict] = {}
    br_l: ClassVar[dict] = {}
    io_l: ClassVar[dict] = {}
    jumps: ClassVar[dict] = {}

    signal_handler: ClassVar[dict] = {}

    def __init__(self, code, input_token, start_of_variables):
        self.data_stack = Stack(STACK_SIZE)
        self.alu = ALU()
        self.instruction_register = {}
        self.buffer_register = 0
        self.memory = Memory(code, start_of_variables)
        self.pc = 1
        self.input_buffer = input_token
        self.output_buffer = []

        self.ar_l = {
            ARLatch.PC: lambda: self.set_address_register(self.pc),
            ARLatch.TOS: lambda: self.set_address_register(self.top_of_stack),
        }
        self.mem_s = {
            MEMSignal.READ: lambda: self.memory.read(self.address_register),
            MEMSignal.WRITE: lambda: self.memory.write(self.address_register),
            MEMSignal.TOS: lambda: self.set_memory(self.top_of_stack),
        }
        self.ir_l = {
            IRLatch.MEM: lambda: self.mem_value_to_ir(),
        }
        self.alu_v = {
            ALUValues.VAR: lambda: self.alu_values_get(),
        }
        self.alu_l = {
            AluLatch.SUM: lambda: self.alu.do_operation(0),
            AluLatch.SUB: lambda: self.alu.do_operation(1),
            AluLatch.MUL: lambda: self.alu.do_operation(2),
            AluLatch.DIV: lambda: self.alu.do_operation(3),
            AluLatch.MOD: lambda: self.alu.do_operation(4),
            AluLatch.NOT_EQ: lambda: self.alu.do_operation(5),
            AluLatch.EQ: lambda: self.alu.do_operation(6),
            AluLatch.MORE: lambda: self.alu.do_operation(7),
            AluLatch.LESS: lambda: self.alu.do_operation(8),
        }
        self.tos_l = {
            TosLatch.ALU: lambda: self.set_top_of_stack(self.alu.value),
            TosLatch.BR: lambda: self.set_top_of_stack(self.buffer_register),
            TosLatch.MEM: lambda: self.set_top_of_stack(
                self.memory.memory[self.address_register]
            ),
            TosLatch.IR: lambda: self.set_top_of_stack(
                int(self.instruction_register["arg"])
            ),
            TosLatch.IR_VAR: lambda: self.set_top_of_stack(
                int(self.instruction_register["arg"]) + self.memory.start_of_variables
            ),
        }
        self.pc_l = {
            PCLatch.IR: lambda: self.set_pc(self.instruction_register["arg"]),
            PCLatch.INC: lambda: self.inc_pc(),
        }
        self.ds_l = {
            DSLatch.Push: lambda: self.push_value(),
            DSLatch.Pop: lambda: self.pop_value(),
        }
        self.br_l = {
            BRLatch.DS: lambda: self.set_bg(self.pop_value()),
        }
        self.io_l = {
            IOLatch.PRINT: lambda: self.print(),
            IOLatch.READ: lambda: self.read(),
            IOLatch.EMIT: lambda: self.emit(),
        }
        self.jumps = {
            JUMPS.JZS: lambda: self.jmpz(),
            JUMPS.JMP: lambda: self.jmp(),
        }

        self.signal_handler = {
            ARLatch: self.ar_l,
            MEMSignal: self.mem_s,
            IRLatch: self.ir_l,
            ALUValues: self.alu_v,
            AluLatch: self.alu_l,
            TosLatch: self.tos_l,
            PCLatch: self.pc_l,
            DSLatch: self.ds_l,
            BRLatch: self.br_l,
            IOLatch: self.io_l,
            JUMPS: self.jumps,
        }

    def execute(self, signal):
        """print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        print(signal)
        print(type(signal))
        print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")"""
        # print(self.signal_handler.get(type(signal)))
        self.signal_handler.get(type(signal)).get(signal)()

    def push_value(self):
        self.data_stack.push(self.top_of_stack)

    def pop_value(self):
        return self.data_stack.pop()

    def set_bg(self, data):
        self.buffer_register = data

    def write_buffer_register(self):
        self.buffer_register = self.pop_value()

    def mem_value_to_ir(self):
        if isinstance(self.memory.value, int):
            self.instruction_register = {"arg": self.memory.value}
        else:
            self.instruction_register = self.memory.value

    def set_top_of_stack(self, data):
        self.top_of_stack = data

    def set_pc(self, data):
        self.pc = data

    def inc_pc(self):
        self.pc += 1

    def alu_values_get(self):
        self.alu.first_value = self.top_of_stack
        self.alu.second_value = self.data_stack.pop()

    def set_address_register(self, data):
        self.address_register = data

    def set_memory(self, data):
        self.memory.value = data

    def print(self):
        self.output_buffer.append(str(self.top_of_stack))
        logging.debug(
            "output: " + "".join(self.output_buffer) + "<<" + str(self.top_of_stack)
        )

    def read(self):
        if len(self.input_buffer) == 0:
            logging.warning("No input from user!")
            self.top_of_stack = 0
        else:
            self.top_of_stack = ord(self.input_buffer.pop(0))
            logging.debug("input: " + chr(self.top_of_stack))

    def emit(self):
        self.output_buffer.append(chr(self.top_of_stack))
        logging.debug(
            "output: " + "".join(self.output_buffer) + "<<" + chr(self.top_of_stack)
        )

    def jmpz(self):
        if self.alu.z_flag == 1:
            self.pc = self.top_of_stack

    def jmp(self):
        self.pc = self.top_of_stack
