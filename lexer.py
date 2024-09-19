from opcode import *
from utils import *

operator = {
    "+",
    "-",
    "*",
    "/",
    "mod",
    "dup",
    "drop",
    "swap",
    "begin",
    "until",
    "=",
    "!=",
    ">",
    "<",
    ".",
    "exit",
    "!",
    "@",
    "#",
    "if",
    "else",
    "endif",
    "emit",
}

variable_names = {}
vars_count = []


def parse_terms(text):
    """
        Transform input to list of terms
    """
    var_counter = 1
    terms = []
    
    procedures = {}
    procedure_name = ""
    is_procedure = False
    need_procedure_name = False
    
    branch_stack = 0
    loop_stack = 0
    
    for line, line in enumerate(text.split("\n"), 1):
        if line != "":
            line_words = line.strip().split(" ")
            for word_num, word in enumerate(line.strip().split(" "), 1):
                if need_procedure_name:
                    procedure_name = str(word)
                    procedures[procedure_name] = []
                    need_procedure_name = False
                elif is_number(word) or word in operator:
                    if is_procedure:
                        procedures[procedure_name].append(Term(line, word_num, word))
                    else:
                        terms.append(Term(line, word_num, word))
                elif word == "buffer":
                    if line_words[1] not in variable_names:
                        variable_names[line_words[1]] = var_counter
                        for i in range(int(line_words[2])):
                            vars_count.append(word)
                        var_counter += int(line_words[2])
                        break
                    if is_procedure:
                        exception_noarg("buffer in procedure")
                elif word == ":":
                    if branch_stack == 0 and loop_stack == 0:
                        if not is_procedure:
                            is_procedure = True
                            need_procedure_name = True
                        else:
                            exception_by_lex("nested procedure", line, word_num, word)
                    else:
                        if branch_stack == 0:
                            exception_by_lex("procedure in branch", line, word_num, word)
                        if loop_stack == 0:
                            exception_by_lex("procedure in loop", line, word_num, word)
                elif word == ";":
                    if branch_stack == 0 and loop_stack == 0:
                        if is_procedure:
                            is_procedure = False
                        else:
                            exception_by_lex("cannot end procedure", line, word_num, word)
                    else:
                        if branch_stack == 0:
                            exception_by_lex("need closing branch before end procedure", line, word_num, word)
                        if loop_stack == 0:
                            exception_by_lex("need closing loop before end procedure", line, word_num, word)
                elif word in procedures.keys():
                    for procedure_term in procedures[word]:
                        terms.append(procedure_term)
                elif word[0:2] == '."':
                    break
                else:
                    if line_words[-1] == "!" or line_words[-1] == "@":
                        if len(line_words) == 2 or len(line_words) == 3:
                            if word not in variable_names:
                                variable_names[word] = var_counter
                                vars_count.append(word)
                                var_counter += 1
                            if is_procedure:
                                procedures[procedure_name].append(Term(line, word_num, word))
                            else:
                                terms.append(Term(line, word_num, word))
                        if len(line_words) == 5:
                            if is_procedure:
                                procedures[procedure_name].append(Term(line, word_num, line.strip()))
                                break
                            terms.append(Term(line, word_num, line.strip()))
                            break
                    else:
                        exception_by_lex("invalid input", line, word_num, word)

                if word == "if":
                    branch_stack -= 1
                if word == "endif":
                    branch_stack += 1
                if word == "begin":
                    loop_stack -= 1
                if word == "until":
                    loop_stack += 1
            if line[0:2] == '."':
                variable_names[line[3:-1]] = var_counter
                var_counter += len(line[3:-1])
                terms.append(Term(line, 1, line))
    if branch_stack < 0:
        exception_noarg("not balanced branches")
    if loop_stack < 0:
        exception_noarg("not balanced loops")
    return terms
