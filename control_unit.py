import logging
from typing import ClassVar
from data_path import *
from utils import *

from signals import *


def opcode2microcode(opcode):
    return {
        Opcode.SUM: 2,
        Opcode.SUB: 4,
        Opcode.MUL: 6,
        Opcode.DIV: 8,
        Opcode.MOD: 10,
        Opcode.DUP: 12,
        Opcode.DROP: 14,
        Opcode.SWAP: 16,
        Opcode.EQ: 19,
        Opcode.MORE: 21,
        Opcode.LESS: 23,
        Opcode.PUSH: 25,
        Opcode.ADDR_ON_TOP: 27,
        Opcode.SAVE_VAR: 29,
        Opcode.VAR_ON_TOP: 32,
        Opcode.JZS: 35,
        Opcode.JMP: 38,
        Opcode.PRINT: 41,
        Opcode.READ: 44,
        Opcode.EMIT: 46,
        Opcode.HALT: 49,
        Opcode.NOT_EQ: 50,
    }.get(opcode)


microcode = [
    # Fetch next Instruction
    [ARLatch.PC, MEMSignal.READ, MCAdrLatch.INC],
    [IRLatch.MEM, Instruction.INC, MCAdrLatch.IR],
    #  Microcode Table
    [ALUValues.VAR, AluLatch.SUM, MCAdrLatch.INC],
    [TosLatch.ALU, PCLatch.INC, Instruction.INC, MCAdrLatch.ZERO],
    [ALUValues.VAR, AluLatch.SUB, MCAdrLatch.INC],
    [TosLatch.ALU, PCLatch.INC, Instruction.INC, MCAdrLatch.ZERO],
    [ALUValues.VAR, AluLatch.MUL, MCAdrLatch.INC],
    [TosLatch.ALU, PCLatch.INC, Instruction.INC, MCAdrLatch.ZERO],
    [ALUValues.VAR, AluLatch.DIV, MCAdrLatch.INC],
    [TosLatch.ALU, PCLatch.INC, Instruction.INC, MCAdrLatch.ZERO],
    [ALUValues.VAR, AluLatch.MOD, MCAdrLatch.INC],
    [TosLatch.ALU, PCLatch.INC, Instruction.INC, MCAdrLatch.ZERO],
    [DSLatch.Push, MCAdrLatch.INC],
    [PCLatch.INC, Instruction.INC, MCAdrLatch.ZERO],
    [DSLatch.Pop, MCAdrLatch.INC],
    [PCLatch.INC, Instruction.INC, MCAdrLatch.ZERO],
    [BRLatch.DS, MCAdrLatch.INC],
    [DSLatch.Push, TosLatch.BR, MCAdrLatch.INC],
    [PCLatch.INC, Instruction.INC, MCAdrLatch.ZERO],
    [ALUValues.VAR, AluLatch.EQ, MCAdrLatch.INC],
    [TosLatch.ALU, PCLatch.INC, Instruction.INC, MCAdrLatch.ZERO],
    [ALUValues.VAR, AluLatch.MORE, MCAdrLatch.INC],
    [TosLatch.ALU, PCLatch.INC, Instruction.INC, MCAdrLatch.ZERO],
    [ALUValues.VAR, AluLatch.LESS, MCAdrLatch.INC],
    [TosLatch.ALU, PCLatch.INC, Instruction.INC, MCAdrLatch.ZERO],
    [DSLatch.Push, TosLatch.IR, MCAdrLatch.INC],
    [PCLatch.INC, Instruction.INC, MCAdrLatch.ZERO],
    [DSLatch.Push, TosLatch.IR_VAR, MCAdrLatch.INC],
    [PCLatch.INC, Instruction.INC, MCAdrLatch.ZERO],
    [ARLatch.TOS, BRLatch.DS, TosLatch.BR, MEMSignal.TOS, MCAdrLatch.INC],
    [MEMSignal.WRITE, BRLatch.DS, TosLatch.BR, MCAdrLatch.INC],
    [PCLatch.INC, Instruction.INC, MCAdrLatch.ZERO],
    [ARLatch.TOS, MEMSignal.READ, MCAdrLatch.INC],
    [IRLatch.MEM, TosLatch.IR, MCAdrLatch.INC],
    [PCLatch.INC, Instruction.INC, MCAdrLatch.ZERO],
    [DSLatch.Push, TosLatch.IR, JUMPS.JZS, MCAdrLatch.INC],
    [DSLatch.Pop, BRLatch.DS, TosLatch.BR, MCAdrLatch.INC],
    [PCLatch.INC, Instruction.INC, MCAdrLatch.ZERO],
    [DSLatch.Push, TosLatch.IR, JUMPS.JMP, MCAdrLatch.INC],
    [BRLatch.DS, TosLatch.BR, MCAdrLatch.INC],
    [PCLatch.INC, Instruction.INC, MCAdrLatch.ZERO],
    [IOLatch.PRINT, MCAdrLatch.INC],
    [BRLatch.DS, TosLatch.BR, MCAdrLatch.INC],
    [PCLatch.INC, Instruction.INC, MCAdrLatch.ZERO],
    [DSLatch.Push, MCAdrLatch.INC],
    [IOLatch.READ, Instruction.INC, PCLatch.INC, MCAdrLatch.ZERO],
    [IOLatch.EMIT, MCAdrLatch.INC],
    [BRLatch.DS, TosLatch.BR, MCAdrLatch.INC],
    [PCLatch.INC, Instruction.INC, MCAdrLatch.ZERO],
    [Instruction.INC, PROG.HALT],
    [ALUValues.VAR, AluLatch.NOT_EQ, MCAdrLatch.INC],
    [TosLatch.ALU, PCLatch.INC, Instruction.INC, MCAdrLatch.ZERO],
]


class CU:
    mc_adr = None
    datapath = None
    tick = None
    instruction_count = None
    signal_handlers: ClassVar[dict] = {}
    mc_adr_l: ClassVar[dict] = {}

    def __init__(self, datapath):
        self.mc_adr = 0
        self.datapath = datapath
        self.tick = 0
        self.instruction_count = 0
        self.mc_adr_l = {
            MCAdrLatch.IR: lambda: self.set_adr(opcode2microcode(self.datapath.instruction_register["opcode"])),
            MCAdrLatch.INC: lambda: self.mc_adr_inc(),
            MCAdrLatch.ZERO: lambda: self.set_adr(0)
        }

    def __repr__(self, signal):
        return (
            "TICK: {:4} SIGNAL: {:15} AR: {:3} PC: {:3}  MC_ADR: {:2}  TOS: {:6} Z: {:1} N: {:1} V: {:1} DS: {}"
        ).format(
            str(self.tick),
            str(signal),
            str(self.mc_adr),
            str(self.datapath.pc),
            str(self.datapath.address_register),
            str(self.datapath.top_of_stack) if self.datapath.top_of_stack is not None else "0",
            str(self.datapath.alu.z_flag),
            str(self.datapath.alu.n_flag),
            str(self.datapath.alu.v_flag),
            self.datapath.data_stack.stack,
        )

    def inc_tick(self):
        self.tick += 1

    def inc_instruction_count(self):
        self.instruction_count += 1

    def execute_instruction(self, signals):
        for signal in signals:
            if isinstance(signal, PROG):
                raise StopIteration
            if isinstance(signal, MCAdrLatch):
                self.mc_adr_latch(signal)
            elif isinstance(signal, Instruction):
                self.inc_instruction_count()
            else:
                getattr(self.datapath, "execute")(signal)
            logging.debug("%s", self.__repr__(signal))
            self.inc_tick()

    def mc_adr_inc(self):
        self.mc_adr += 1

    def set_adr(self, data):
        self.mc_adr = data

    def mc_adr_latch(self, signal):
        '''print("------------------------------------------------------------------------------------------------")
        print(self.mc_adr)
        print(signal)
        print(self.mc_adr_l[signal])
        print("------------------------------------------------------------------------------------------------")'''
        self.mc_adr_l[signal]()

    def run_machine(self):
        try:
            while self.instruction_count < INSTRUCTION_LIMIT:
                self.execute_instruction(microcode[self.mc_adr])
        except StopIteration:
            pass
        except OSError:
            pass
        output = ""
        for string in "".join(self.datapath.output_buffer).split("\n"):
            tab = '\t'
            output += f"{4 * tab}{string}\n"
        logging.debug("out: \n" + output[0:-1])
        return self.datapath.output_buffer, self.instruction_count, self.tick
