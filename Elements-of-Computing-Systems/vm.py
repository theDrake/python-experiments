#!usr/bin/python2

#------------------------------------------------------------------------------
#    Filename: vm.py
#
#     Authors: David C. Drake (http://davidcdrake.com) and Remington Scow
#
# Description: A 'CodeWriter' class and a collection of funtions for parsing
#              and translating instructions from a high-level, stack-based,
#              Virtual Machine language (VM) into the Hack assembly language
#              according to the specifications outlined in "The Elements of
#              Computing Systems," by Nisan and Schocken (MIT Press, 2005).
#              Developed using Python 2.7.
#------------------------------------------------------------------------------

import sys
import os

DEBUG = False

COMMANDS = {
    'add':      0,
    'sub':      0,
    'neg':      0,
    'eq':       0,
    'gt':       0,
    'lt':       0,
    'and':      0,
    'or':       0,
    'not':      0,
    'pop':      2,
    'push':     2,
    'label':    1,
    'goto':     1,
    'if-goto':  1,
    'function': 2,
    'call':     2,
    'return':   0
}

SEGMENTS = {
    'argument': True,
    'local':    True,
    'static':   True,
    'constant': True,
    'this':     True,
    'that':     True,
    'pointer':  True,
    'temp':     True
}

SYMBOLS = {
    'SP':     '0',
    'LCL':    '1',
    'ARG':    '2',
    'THIS':   '3',
    'THAT':   '4',
    'R0':     '0',
    'R1':     '1',
    'R2':     '2',
    'R3':     '3',
    'R4':     '4',
    'R5':     '5',
    'R6':     '6',
    'R7':     '7',
    'R8':     '8',
    'R9':     '9',
    'R10':    '10',
    'R11':    '11',
    'R12':    '12',
    'R13':    '13',
    'R14':    '14',
    'R15':    '15',
    'SCREEN': '16384',
    'KBD':    '24576'
}

#------------------------------------------------------------------------------
#       Class: CodeWriter
#
# Description: Generates Hack assembly code corresponding to given VM commands
#              and writes them to an output file.
#------------------------------------------------------------------------------
class CodeWriter:
    #--------------------------------------------------------------------------
    #      Method: __init__
    #
    # Description: Initializes the CodeWriter object.
    #
    #      Inputs: fout - An open output file handle.
    #
    #     Outputs: None.
    #--------------------------------------------------------------------------
    def __init__(self, fout):
        self.fout = fout
        self.sourceFile = ''
        self.currentFunction = ''
        self.returnAddressCounter = 0
        self.eqCounter = 0
        self.ltCounter = 0
        self.gtCounter = 0

    #--------------------------------------------------------------------------
    #      Method: setFileName
    #
    # Description: Sets the name of the current VM source file.
    #
    #      Inputs: filename - Name of a VM source file.
    #
    #     Outputs: The name of the newly-assigned VM source file.
    #--------------------------------------------------------------------------
    def setFileName(self, filename):
        self.sourceFile = filename
        self.write('\n// Source file: "' + filename + '.vm"')
        return self.sourceFile

    #--------------------------------------------------------------------------
    #      Method: write
    #
    # Description: Generic function for writing a string to the output file.
    #
    #      Inputs: text - A string to write to the output file.
    #
    #     Outputs: None. However, a string is written to the output file.
    #--------------------------------------------------------------------------
    def write(self, text):
        print >>self.fout, text

    #--------------------------------------------------------------------------
    #      Method: writePushPop
    #
    # Description: Generates Hack assembly code for a given 'push' or 'pop'
    #              command and writes it to the output file.
    #
    #      Inputs: command - Either 'push' or 'pop'.
    #              segment - Name of the relevant segment.
    #              index   - Integer value for indexing the segment.
    #
    #     Outputs: None. However, a line of assembly code is written to the
    #              output file.
    #--------------------------------------------------------------------------
    def writePushPop(self, command, segment, index):
        # Write the original VM code to the output file as a comment:
        self.write('\n// ' + command + ' ' + segment + ' ' + str(index))

        # Assembly code for 'push' commands:
        if command == 'push':
            if segment == 'constant':
                self.write('@' + str(index))
                self.write('D=A')
            elif segment == 'static':
                self.write('@' + self.sourceFile + '.' + str(index))
                self.write('D=M')
            elif segment == 'pointer':
                if index == 0:
                    self.write('@THIS')
                elif index == 1:
                    self.write('@THAT')
                else:
                    fail('Error: "' + index + '" is an invalid index for ' +
                         'pointer segment (should be 0 or 1).');
                self.write('D=M')
            elif segment == 'temp':
                if index > 6:
                    fail('Error: "' + index + '" is an invalid index for ' +
                         'the temp segment (should be within 0-6, inclusive).')
                self.write('@R' + str(5 + index))
                self.write('D=M')
            elif segment == 'local' or segment == 'argument' or \
                 segment == 'this' or segment == 'that':
                self.write('@' + str(index))
                self.write('D=A')
                if segment == 'local':
                    self.write('@LCL')
                elif segment == 'argument':
                    self.write('@ARG')
                else: # 'this' or 'that'
                    self.write('@' + SYMBOLS[segment.upper()])
                self.write('D=D+M')
                self.write('A=D')
                self.write('D=M')
            else:
                fail('Error: "' + segment + '" is an invalid segment name.')
            self.write('@SP')
            self.write('A=M')
            self.write('M=D')
            self.write('@SP')
            self.write('M=M+1')

        # Assembly code for 'pop' commands:
        elif command == 'pop':
            if segment == 'constant':
                fail('Error: "constant" is an invalid segment name for a ' +
                     '"pop" command.')
            elif segment == 'static' or segment == 'pointer' or \
               segment == 'temp':
                self.write("@SP")
                self.write('AM=M-1')
                self.write('D=M')
                if segment == 'static':
                    self.write('@' + self.sourceFile + '.' + str(index))
                elif segment == 'pointer':
                    if index == 0:
                        self.write('@THIS')
                    elif index == 1:
                        self.write('@THAT')
                    else:
                        fail('Error: "' + index + '" is an invalid index ' +
                             'for pointer segment (should be 0 or 1).');
                elif segment == 'temp':
                    if index > 6:
                        fail('Error: "' + index + '" is an invalid index ' +
                             'for the temp segment (should be within 0-6, ' +
                             'inclusive).')
                    self.write('@R' + str(5 + index))
            elif segment == 'local' or segment == 'argument' or \
                 segment == 'this' or segment == 'that':
                if segment == 'local':
                    self.write('@LCL')
                elif segment == 'argument':
                    self.write('@ARG')
                elif segment == 'this':
                    self.write('@THIS')
                else: #that
                    self.write('@THAT')
                self.write('D=M')
                self.write('@' + str(index))
                self.write('D=D+A')
                self.write('@R13')
                self.write('M=D')
                self.write('@SP')
                self.write('AM=M-1')
                self.write('D=M')
                self.write('@R13')
                self.write('A=M')
            else:
                fail('Error: "' + segment + '" is an invalid segment name.')
            self.write('M=D')

    #--------------------------------------------------------------------------
    #      Method: writeArithmetic
    #
    # Description: Generates Hack assembly code for a given arithmetic command
    #              and writes it to the output file.
    #
    #      Inputs: command - Either 'add', 'sub', 'neg', 'and', 'or', 'not',
    #                        'eq', 'lt', or 'gt'.
    #
    #     Outputs: None. However, a line of assembly code is written to the
    #              output file.
    #--------------------------------------------------------------------------
    def writeArithmetic(self, command):
        # Write the original VM code to the output file as a comment:
        self.write('\n// ' + command)

        if command == 'add':
            self.write('@SP')
            self.write('AM=M-1')
            self.write('D=M')
            self.write('A=A-1')
            self.write('M=D+M')
        elif command == 'sub':
            self.write('@SP')
            self.write('AM=M-1')
            self.write('D=M')
            self.write('A=A-1')
            self.write('M=M-D')
        elif command == 'neg':
            self.write('@SP')
            self.write('A=M-1')
            self.write('M=-M')
        elif command == 'and':
            self.write('@SP')
            self.write('AM=M-1')
            self.write('D=M')
            self.write('A=A-1')
            self.write('M=D&M')
        elif command == 'or':
            self.write('@SP')
            self.write('AM=M-1')
            self.write('D=M')
            self.write('A=A-1')
            self.write('M=D|M')
        elif command == 'not':
            self.write('@SP')
            self.write('A=M-1')
            self.write('M=!M')
        elif command == 'eq':
            self.eqCounter += 1
            self.write('@_EQ_' + str(self.eqCounter))
            self.write('D=A')
            self.write('@_EQ')
            self.write('0;JMP')
            self.write('(_EQ_' + str(self.eqCounter) + ')')
        elif command == 'lt':
            self.ltCounter += 1
            self.write('@_LT_' + str(self.ltCounter))
            self.write('D=A')
            self.write('@_LT')
            self.write('0;JMP')
            self.write('(_LT_' + str(self.ltCounter) + ')')
        elif command == 'gt':
            self.gtCounter += 1
            self.write('@_GT_' + str(self.gtCounter))
            self.write('D=A')
            self.write('@_GT')
            self.write('0;JMP')
            self.write('(_GT_' + str(self.gtCounter) + ')')
        else:
            fail('Error: invalid command sent to ' +
                 'CodeWriter.writeArithmetic(): "' + command + '"')

    #--------------------------------------------------------------------------
    #      Method: writePost
    #
    # Description: Adds comparison subroutines to the output file, if needed.
    #
    #      Inputs: None.
    #
    #     Outputs: None. However, assembly code subroutines may be written to
    #              the output file.
    #--------------------------------------------------------------------------
    def writePost(self):
        if self.eqCounter > 0 or self.gtCounter > 0 or self.ltCounter > 0:
            self.write('@END')
            self.write('0;JMP')

        if self.eqCounter > 0:
            self.write('\n// The "equals" subroutine:')
            self.write('(_EQ)')
            self.write('@R15')
            self.write('M=D')            # Store the return address.
            self.write('@SP')
            self.write('AM=M-1')
            self.write('D=M')
            self.write('@SP')
            self.write('AM=M-1')
            self.write('D=M-D')          # Subtract two popped values.
            self.write('@_EQ_NOT')
            self.write('D;JNE')
            self.write('D=-1')           # If equal, push -1.
            self.write('@_EQ_COMMON')
            self.write('0;JMP')
            self.write('(_EQ_NOT)')
            self.write('D=0')            # If not equal, push 0.
            self.write('(_EQ_COMMON)')
            self.write('@SP')
            self.write('M=M+1')          # Add 1 to *SP.
            self.write('A=M-1')          # Set A to *SP - 1.
            self.write('M=D')
            self.write('@R15')
            self.write('A=M')
            self.write('0;JMP')          # Return.

        if self.ltCounter > 0:
            self.write('\n// The "less than" subroutine:')
            self.write('(_LT)')
            self.write('@R15')
            self.write('M=D')            # Store the return address.
            self.write('@SP')
            self.write('AM=M-1')
            self.write('D=M')
            self.write('@SP')
            self.write('AM=M-1')
            self.write('D=M-D')          # Subtract two popped values.
            self.write('@_LT_NOT')
            self.write('D;JGE')
            self.write('D=-1')           # If less than, push -1.
            self.write('@_LT_COMMON')
            self.write('0;JMP')
            self.write('(_LT_NOT)')
            self.write('D=0')            # Otherwise, push 0.
            self.write('(_LT_COMMON)')
            self.write('@SP')
            self.write('M=M+1')          # Add 1 to *SP.
            self.write('A=M-1')          # Set A to *SP - 1.
            self.write('M=D')
            self.write('@R15')
            self.write('A=M')
            self.write('0;JMP')          # Return.

        if self.gtCounter > 0:
            self.write('\n// The "greater than" subroutine:')
            self.write('(_GT)')
            self.write('@R15')
            self.write('M=D')            # Store the return address.
            self.write('@SP')
            self.write('AM=M-1')
            self.write('D=M')
            self.write('@SP')
            self.write('AM=M-1')
            self.write('D=M-D')          # Subtract two popped values.
            self.write('@_GT_NOT')
            self.write('D;JLE')
            self.write('D=-1')           # If greater than, push -1.
            self.write('@_GT_COMMON')
            self.write('0;JMP')
            self.write('(_GT_NOT)')
            self.write('D=0')            # Otherwise, push 0.
            self.write('(_GT_COMMON)')
            self.write('@SP')
            self.write('M=M+1')          # Add 1 to *SP.
            self.write('A=M-1')          # Set A to *SP - 1.
            self.write('M=D')
            self.write('@R15')
            self.write('A=M')
            self.write('0;JMP')          # Return.

        if self.eqCounter > 0 or self.gtCounter > 0 or self.ltCounter > 0:
            self.write('(END)')
            self.write('0;JMP')

    #--------------------------------------------------------------------------
    #      Method: writeLabel
    #
    # Description: Writes the assembly code for a given label.
    #
    #      Inputs: label - A string containing the name of the label.
    #
    #     Outputs: None. However, it writes assembly code to the output file.
    #--------------------------------------------------------------------------
    def writeLabel(self, label):
        self.write('(' + self.currentFunction + '$' + label + ')')

    #--------------------------------------------------------------------------
    #      Method: writeGoto
    #
    # Description: Writes the assembly code for 'goto' commands.
    #
    #      Inputs: label - A string containing the name of the label.
    #
    #     Outputs: None. However, assembly code is written to the output file.
    #--------------------------------------------------------------------------
    def writeGoto(self, label):
        # Write the original VM code to the output file as a comment:
        self.write('\n// goto ' + str(label))

        self.write('@' + self.currentFunction + '$' + label)
        self.write('0;JMP')

    #--------------------------------------------------------------------------
    #      Method: writeIf
    #
    # Description: Writes the assembly code for 'if-goto' commands.
    #
    #      Inputs: label - A string containing the name of the label.
    #
    #     Outputs: None. However, assembly code is written to the output file.
    #--------------------------------------------------------------------------
    def writeIf(self, label):
        # Write the original VM code to the output file as a comment:
        self.write('\n// if-goto ' + str(label))

        self.write('@SP')
        self.write('AM=M-1')
        self.write('D=M')
        self.write('@' + self.currentFunction + '$' + label)
        self.write('D;JEQ')

    #--------------------------------------------------------------------------
    #      Method: writeCall
    #
    # Description: Writes the assembly code for a 'call' command.
    #
    #      Inputs: functionName - Name of the called function.
    #              numArgs      - Number of arguments (which should already
    #                             have been pushed onto the stack).
    #
    #     Outputs: None. However, assembly code is written to the output file.
    #--------------------------------------------------------------------------
    def writeCall(self, functionName, numArgs):
        # Write the original VM code to the output file as a comment:
        self.write('\n// call ' + functionName + ' ' + str(numArgs))

        returnAddressLabel = functionName + \
                             str(self.returnAddressCounter)
        self.returnAddressCounter += 1

        # Push the return address onto the stack:
        self.writePushPop('push', 'constant', returnAddressLabel)

        # Push the current values of LCL, ARG, THIS, and THAT onto the stack:
        segments = ['LCL', 'ARG', 'THIS', 'THAT']
        for s in segments:
            self.write('@' + s)
            self.write('D=M')
            self.write('@SP')
            self.write('A=M')
            self.write('M=D')
            self.write('@SP')
            self.write('M=M+1')

        # ARG = SP - numArgs - 5
        self.write('@SP')
        self.write('D=M')
        self.write('@'+ str(int(numArgs)))
        self.write('D=D-A')
        self.write('@5')
        self.write('D=D-A')
        self.write('@ARG')
        self.write('M=D')

        # LCL = SP
        self.write('@SP')
        self.write('D=M')
        self.write('@LCL')
        self.write('M=D')

        self.write('@' + functionName)
        self.write('0;JMP')

        self.write('(' + returnAddressLabel + ')')

    #--------------------------------------------------------------------------
    #      Method: writeReturn
    #
    # Description: Writes the assembly code for a 'return' command.
    #
    #      Inputs: None.
    #
    #     Outputs: None. However, assembly code is written to the output file
    #--------------------------------------------------------------------------
    def writeReturn(self):
        # Write the original VM code to the output file as a comment:
        self.write('\n// return')

        # Find the return address and store it in a temporary variable:
        self.write('@LCL')
        self.write('D=M')
        self.write('@5')
        self.write('A=D-A')
        self.write('D=M')
        self.write('@R13')
        self.write('M=D')

        # Put the return value in the place of argument 0:
        self.write('@SP')
        self.write('A=M-1')
        self.write('D=M')
        self.write('@ARG')
        self.write('A=M')
        self.write('M=D')

        # Restore the previous SP value:
        self.write('@ARG')
        self.write('D=M+1')
        self.write('@SP')
        self.write('M=D')

        # Restore the previous THAT value:
        self.write('@LCL')
        self.write('AM=M-1')
        self.write('D=M')
        self.write('@THAT')
        self.write('M=D')

        # Restore the previous THIS value:
        self.write('@LCL')
        self.write('AM=M-1')
        self.write('D=M')
        self.write('@THIS')
        self.write('M=D')

        # Restore the previous ARG value:
        self.write('@LCL')
        self.write('AM=M-1')
        self.write('D=M')
        self.write('@ARG')
        self.write('M=D')

        # Restore the previous LCL value:
        self.write('@LCL')
        self.write('AM=M-1')
        self.write('D=M')
        self.write('@LCL')
        self.write('M=D')

        # Go back to the location specified by the return address:
        self.write('@R13')
        self.write('A=M')
        self.write('0;JMP')

    #--------------------------------------------------------------------------
    #      Method: writeFunction
    #
    # Description: Writes the assembly code definition of a given function.
    #
    #      Inputs: functionName - Name of the function to be defined.
    #              numLocals    - Number of local variables used by the
    #                             function.
    #
    #     Outputs: None. However, assembly code is written to the output file.
    #--------------------------------------------------------------------------
    def writeFunction(self, functionName, numLocals):
        # Write the original VM code to the output file as a comment:
        self.write('\n// function ' + functionName + ' ' + str(numLocals))

        self.currentFunction = functionName
        self.write('(' + functionName + ')')
        for i in range(int(numLocals)):
            self.writePushPop('push', 'constant', 0)

#------------------------------------------------------------------------------
#    Function: fail
#
# Description: Prints an informative error message, then exits the program.
#
#      Inputs: errorMessage - A string specifying the type of error.
#
#     Outputs: None.
#------------------------------------------------------------------------------
def fail(error_message):
    sys.stderr.write(error_message)
    sys.exit(-1)

#------------------------------------------------------------------------------
#    Function: isConstant
#
# Description: Determines whether a given string could legally serve as an
#              integer constant within VM or the Hack assembly language.
#              Specifically, each character must be a digit and the number's
#              value must lie between 0 and 32,767 (inclusive).
#
#      Inputs: string - A string that might contain a user-defined constant.
#
#     Outputs: 'True' if the string satisfies the basic criteria for a VM or
#              Hack assembly language integer constant, 'False' otherwise.
#------------------------------------------------------------------------------
def isConstant(string):
    return string and string.isdigit() and (0 <= int(string) <= 32767)

#------------------------------------------------------------------------------
#    Function: isSymbol
#
# Description: Determines whether a given string could legally serve as a
#              symbol (i.e., a label or variable) within VM or the Hack
#              assembly language. Specifically, the first character must not be
#              a digit and the other characters (if any) must either be
#              letters, digits, or one of the accepted special characters: '_',
#              '.', '$', or ':'. (Does not determine whether the given string
#              is a reserved word or previously defined label.)
#
#      Inputs: string - A string that might contain a user-defined label or
#                       variable.
#
#     Outputs: 'True' if the string satisfies the basic criteria for a VM or
#              Hack assembly language symbol, 'False' otherwise.
#------------------------------------------------------------------------------
def isSymbol(string):
    if not string or string[0].isdigit():
        return False
    allowedChar = ['_', '.', '$', ':']
    for i in range(len(string)):
        if not string[i].isalnum() and string[i] not in allowedChar:
            return False
    return True

#------------------------------------------------------------------------------
#    Function: processFile
#
# Description: Processes a list of tuples containing VM commands and arguments.
#
#      Inputs: codeWriter - A CodeWriter object.
#              filename   - Name of the VM source file.
#              commands   - List of tuples containing commands and arguments.
#
#     Outputs: None.
#------------------------------------------------------------------------------
def processFile(codeWriter, filename, commands):
    codeWriter.setFileName(filename[:filename.find('.vm')])
    for command in commands:
        if command[0] == 'push' or command[0] == 'pop':
            codeWriter.writePushPop(command[0], command[1], int(command[2]))
        elif command[0] == 'label':
            codeWriter.writeLabel(command[1])
        elif command[0] == 'goto':
            codeWriter.writeGoto(command[1])
        elif command[0] == 'if-goto':
            codeWriter.writeIf(command[1])
        elif command[0] == 'call':
            codeWriter.writeCall(command[1], command[2])
        elif command[0] == 'return':
            codeWriter.writeReturn()
        elif command[0] == 'function':
            codeWriter.writeFunction(command[1], command[2])
        else:
            codeWriter.writeArithmetic(command[0])

#------------------------------------------------------------------------------
#    Function: parseFile
#
# Description: Parses a file of VM code, producing a list of tuples containing
#              commands and arguments corresponding to each line of VM code.
#
#      Inputs: filename - Name (or complete path) of a file containing VM code.
#
#     Outputs: A list of tuples representing parsed lines of VM code.
#------------------------------------------------------------------------------
def parseFile(filename):
    fin = open(filename, 'r')
    lines = fin.readlines()
    fin.close()
    parsed_lines = []
    line_number = 1
    for line in lines:
        parsed_line = parseLine(line, line_number)
        if parsed_line:
            if DEBUG:
                print '' + str(parsed_line)
            parsed_lines.append(parsed_line)
        line_number += 1
    return parsed_lines

#------------------------------------------------------------------------------
#    Function: parseLine
#
# Description: Parses a single line of VM code, producing a tuple containing a
#              command and its arguments (if any). If an error is detected
#              within the line of code, a relevant message will be presented
#              and the program will exit.
#
#      Inputs: line        - A string containing a single line of VM code.
#              line_number - The line's line number within the source file.
#
#     Outputs: A tuple containing a command and its arguments (or 'None' if
#              'line' was empty or consisted only of a comment).
#------------------------------------------------------------------------------
def parseLine(line, line_number):
    if DEBUG:
        print '\tParsing line ' + str(line_number) + ': ' + line[:-1]

    # Remove comments and surrounding whitespace:
    if line.find('//') != -1:
        line = line[:line.find('//')]
    line = line.strip()

    # Check for an empty string:
    if not line:
        return None

    line = line.split()

    # Check for a valid command and the correct number of arguments:
    if line[0] in COMMANDS:
        if len(line)-1 is not COMMANDS[line[0]]:
            fail('Error on line ' + str(line_number) + ': "' + str(line[0]) +
                 '" requires ' + str(COMMANDS[line[0]]) +
                 ' arguments, but was given ' + str(len(line)-1) + '.')
    else:
        fail('Error on line ' + str(line_number) + ': "' + str(line[0]) +
             '" is not a valid command.')

    # The first argument (if any) must be a valid symbol:
    if COMMANDS[line[0]] > 0:
        if not isSymbol(line[1]):
            fail('Error on line ' + str(line_number) + ': "' + str(line[1]) +
                 '" is not a valid symbol.')

    # The second argument (if any) must be a valid constant:
    if COMMANDS[line[0]] > 1:
        if not isConstant(line[2]):
            fail('Error on line ' + str(line_number) + ': "' + str(line[1]) +
                 '" is not a valid constant.')

    # The 'push' and 'pop' commands must be followed by a valid segment name
    # (which must not be 'constant' for a 'pop' command):
    if line[0] is 'push' or line[0] is 'pop':
        if line[1] not in SEGMENTS or \
           (line[0] is 'pop' and line[1] is 'constant'):
                fail('Error on line ' + str(line_number) + ': "' + str(line) +
                     '" is an invalid "' + line[0] + '" command.')

    # Labels must not begin with a digit:
    if line[0] is 'label' and not isSymbol(line[1]):
        fail('Error on line ' + str(line_number) + ': "' + str(line[1]) +
             '" is an invalid label.');

    return line

#------------------------------------------------------------------------------
#    Function: main
#
# Description: Processes command line arguments, manages the parsing of one
#              or more VM input files, and then -- if the parsing process
#              completed successfully -- writes an assembly translation to an
#              output file.
#
#      Inputs: sys.argv - A valid input file, or a directory containing one or
#                         more valid input files, must be specified as a
#                         command-line argument.
#
#     Outputs: None. However, if the program completes successfully, an output
#              file will be created. It will have the same name as the input
#              file, but with a '.asm' extension rather than '.vm'.
#------------------------------------------------------------------------------
def main():
    # Check for the correct number of command-line arguments:
    if len (sys.argv) != 2:
        fail('Usage: ' + os.path.basename(sys.argv[0]) +
             ' [directory or filename.vm]')

    # Analyze command-line input to determine which file(s) to translate:
    full_path = os.path.abspath(sys.argv[1])
    file_list = []
    if full_path.endswith('.vm'):
        if not os.path.isfile(full_path):
            fail('Error: "' + os.path.basename(full_path) +
                 '" does not exist.')
        out_filename = full_path[:-len('.vm')] + '.asm'
        file_list.append(full_path)
    elif os.path.isdir(full_path):
        out_filename = os.path.join(full_path,
                                    os.path.basename(full_path) + '.asm')
        files = os.listdir(full_path)
        for name in files:
            full_name = os.path.join(full_path, name)
            if name.endswith('.vm') and os.path.isfile(full_name):
                file_list.append(full_name)
    else:
        fail('Error: "' + os.path.basename(full_path) +
             '" is not a valid directory or .vm file.')
    if DEBUG:
        print 'File list: ' + str(file_list)

    # Read and parse the VM input file(s):
    parsed_files = []
    for filename in file_list:
        print 'Processing "' + os.path.basename(filename) + '"...'
        parsed_files.append((filename, parseFile(filename)))
    print 'Procesing complete.'

    # Write an assembly translation to the output file:
    print 'Writing to "' + os.path.basename(out_filename) + '"...'
    asm_file = open(out_filename, 'w')
    print >>asm_file, '//\n// ' + os.path.basename(out_filename) + '\n//\n'
    writer = CodeWriter(asm_file)

    # Set SP to 256 and call 'sys.init' (necessary to pass tests):
    writer.write('@256')
    writer.write('D=A')
    writer.write('@SP')
    writer.write('M=D')
    writer.write('@5')
    writer.write('D=A')
    writer.write('@SP')
    writer.write('M=M+D')
    writer.write('@Sys.init')
    writer.write('0;JMP')

    for (filename, parsed_file) in parsed_files:
        processFile(writer,
                    os.path.basename(filename),
                    parsed_file)
    writer.writePost()
    asm_file.close()
    print 'Writing complete.'

if __name__ == '__main__':
    main()
