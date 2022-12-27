#!usr/bin/python2

#-------------------------------------------------------------------------------
#    Filename: assembler.py
#
#     Authors: David C. Drake (https://davidcdrake.com) and Shawn Redmond
#
# Description: Functions for parsing and translating a Hack assembly code file
#              to produce a Hack machine code file according to the
#              specifications outlined in "The Elements of Computing Systems,"
#              by Nisan and Schocken (MIT Press, 2005). Developed using Python
#              2.7.
#-------------------------------------------------------------------------------

import sys
import os.path

DEBUG = False

global nextAvailableMemoryLocation

PREDEFINED_SYMBOLS = {
    'SP':     0,
    'LCL':    1,
    'ARG':    2,
    'THIS':   3,
    'THAT':   4,
    'R0':     0,
    'R1':     1,
    'R2':     2,
    'R3':     3,
    'R4':     4,
    'R5':     5,
    'R6':     6,
    'R7':     7,
    'R8':     8,
    'R9':     9,
    'R10':    10,
    'R11':    11,
    'R12':    12,
    'R13':    13,
    'R14':    14,
    'R15':    15,
    'SCREEN': 16384,
    'KBD':    24576,
}

nextAvailableMemoryLocation = PREDEFINED_SYMBOLS['R15'] + 1

VARIABLE_SYMBOLS = {}

LABEL_SYMBOLS = {}

DESTINATIONS = {
    '':    '000',
    'M':   '001',
    'D':   '010',
    'MD':  '011',
    'A':   '100',
    'AM':  '101',
    'AD':  '110',
    'AMD': '111',
}

JUMPS = {
    '':    '000',
    'JGT': '001',
    'JEQ': '010',
    'JGE': '011',
    'JLT': '100',
    'JNE': '101',
    'JLE': '110',
    'JMP': '111',
}

COMPUTATIONS = {
    '0':   '101010',
    '1':   '111111',
    '-1':  '111010',
    'D':   '001100',
    'A':   '110000',
    'M':   '110000',
    '!D':  '001101',
    '!A':  '110001',
    '!M':  '110001',
    '-D':  '001111',
    '-A':  '110011',
    '-M':  '110011',
    'D+1': '011111',
    'A+1': '110111',
    'M+1': '110111',
    'D-1': '001110',
    'A-1': '110010',
    'M-1': '110010',
    'D+A': '000010',
    'D+M': '000010',
    'D-A': '010011',
    'D-M': '010011',
    'A-D': '000111',
    'M-D': '000111',
    'D&A': '000000',
    'D&M': '000000',
    'D|A': '010101',
    'D|M': '010101',
}

#-------------------------------------------------------------------------------
#    Function: parse
#
# Description: Parses a file of Hack assembly code, producing a list of tuples
#              containing essential information about each assembly
#              instruction.
#
#      Inputs: fin - An open file handle containing assembly code.
#
#     Outputs: A list of tuples representing parsed lines of assembly code.
#-------------------------------------------------------------------------------
def parse(fin):
    if DEBUG:
        print 'Parsing file: ' + str(fin)

    if not fin:
        return None

    assemblyCode = fin.readlines()

    parsedAssemblyCode = []
    sourceLineNum = 0
    outputLineNum = 0
    for line in assemblyCode:
        sourceLineNum += 1
        parsedLine = parseLine(line, sourceLineNum)
        if parsedLine:
            outputLineNum += 1
            parsedAssemblyCode.append(parsedLine)

    if DEBUG:
        print 'Parsed assembly code:'
        for line in parsedAssemblyCode:
            print '\t' + str(line)

    return parsedAssemblyCode

#-------------------------------------------------------------------------------
#    Function: parseLine
#
# Description: Parses a single line of Hack assembly code, producing a tuple
#              containing essential information about the associated assembly
#              instruction (or 'None' if the line was empty or only contained a
#              comment). The tuple will take one of the following forms,
#              according to the type of instruction it represents:
#
#                   ('A_INSTRUCTION', symbol, srcline, srclinenumber)
#
#                   ('L_INSTRUCTION', symbol, srcline, srclinenumber)
#
#                   ('C_INSTRUCTION', dest, comp, jump, srcline, srclinenumber)
#
#              If an error is detected within the line of code, a relevant
#              message will be presented and the program will exit.
#
#      Inputs: line    - A string containing a single line of assembly code.
#              lineNum - The line's line number within the source file.
#
#     Outputs: A tuple representing a parsed version of 'line' (or 'None' if
#              'line' was empty or consisted only of a comment).
#-------------------------------------------------------------------------------
def parseLine(line, lineNum):
    if DEBUG:
        print 'Parsing line: ' + line

    # Remove comments as well as leading and trailing whitespace:
    if '//' in line:
        line = line[:line.find('//'):]
    line = line.strip()

    # Check for an empty string:
    if len(line) < 1:
        return None

    # A-instructions:
    if line[0] is '@':
        if DEBUG:
            print 'A-instruction'
        symbol = line[line.find('@') + 1::]
        if not (isSymbol(symbol) or isConstant(symbol)):
            fail('invalid a-instruction', lineNum, line)

        return ('A_INSTRUCTION', symbol, line, lineNum)

    # L-instructions:
    if line[0] is '(' and line[len(line) - 1] is ')':
        if DEBUG:
            print 'L-instruction'
        symbol = line[1:len(line) - 1:]
        if not isSymbol(symbol) or isReservedOrIsLabel(symbol):
            fail('invalid label', lineNum, line)

        return ('L_INSTRUCTION', symbol, line, lineNum)

    # C-instructions:
    if DEBUG:
        print 'C-instruction'
    comp = line
    dest = ''
    if '=' in line:
        dest = line[:line.find('='):]
        if dest not in DESTINATIONS:
            fail('invalid destination', lineNum, line)
        comp = comp[comp.find('=') + 1::]
    jump = ''
    if ';' in line:
        jump = line[line.find(';') + 1::]
        if jump not in JUMPS:
            fail('invalid jump command', lineNum, line)
        comp = comp[:comp.find(';'):]
    if comp not in COMPUTATIONS:
        fail('invalid computation', lineNum, line)

    return ('C_INSTRUCTION', dest, comp, jump, line, lineNum)

#-------------------------------------------------------------------------------
#    Function: processSymbols
#
# Description: Searches for L-instructions (user-defined labels) within a list
#              of parsed Hack assembly instructions. If any are found, they are
#              added to the symbol table with the line number of the next
#              instruction as their value (unless they have already been
#              defined in a previous L-instruction, in which case an error
#              message is presented and the program exits).
#
#      Inputs: parsedCodeList - A list of tuples representing parsed assembly
#                               instructions.
#
#     Outputs: None. However, labels may be added to the LABEL_SYMBOLS
#              dictionary.
#-------------------------------------------------------------------------------
def processSymbols(parsedCodeList):
    if DEBUG:
        print 'Processing symbols in parsed code...'

    lineNum = 0
    for line in parsedCodeList:
        if line[0] is 'L_INSTRUCTION':
            label = line[1]
            if isReservedOrIsLabel(label):
                fail('label defined more than once', line[3], line[2])
            if DEBUG:
                print '\tLabel "' + label + '" set to ' + str(lineNum)
            LABEL_SYMBOLS[label] = lineNum
        else:
            lineNum += 1

#-------------------------------------------------------------------------------
#    Function: translate
#
# Description: Given a list of tuples representing parsed Hack assembly
#              instructions, a list of strings containing corresponding machine
#              code instructions is produced. Only A-instructions and
#              C-instructions are translated: L-instructions are ignored.
#
#      Inputs: parsedCodeList - A list of tuples representing parsed assembly
#                               instructions.
#
#     Outputs: A list of strings containing Hack machine code instructions.
#-------------------------------------------------------------------------------
def translate(parsedCodeList):
    if DEBUG:
        print 'Translating parsed code...'

    machineCode = []
    for line in parsedCodeList:
        if line[0] is not 'L_INSTRUCTION':
            machineCode.append(translateLine(line))

    if DEBUG:
        print 'Translated machine code:'
        for i in range(len(machineCode)):
            print '\tLine ' + str(i) + ': \t' + str(machineCode[i])

    return machineCode

#-------------------------------------------------------------------------------
#    Function: translateLine
#
# Description: Given a list of tuples representing parsed Hack assembly
#              instructions, a list of strings containing corresponding machine
#              code instructions is produced. Only A-instructions and
#              C-instructions are translated: L-instructions are ignored.
#
#      Inputs: line - A tuple representing a parsed assembly instruction.
#
#     Outputs: A string containing a Hack machine code instruction (or an empty
#              string in the case of invalid input).
#-------------------------------------------------------------------------------
def translateLine(line):
    if DEBUG:
        print '\tTranslating line: ' + str(line)

    global nextAvailableMemoryLocation

    instruction = ''

    # A-instructions:
    if line[0] is 'A_INSTRUCTION':
        instruction += '0'
        if isConstant(line[1]):
            value = int(line[1])
        else:
            symbol = line[1]
            if symbol in PREDEFINED_SYMBOLS:
                value = PREDEFINED_SYMBOLS[symbol]
            elif symbol in LABEL_SYMBOLS:
                value = LABEL_SYMBOLS[symbol]
            else:
                if symbol not in VARIABLE_SYMBOLS:
                    VARIABLE_SYMBOLS[symbol] = nextAvailableMemoryLocation
                    nextAvailableMemoryLocation += 1
                value = VARIABLE_SYMBOLS[symbol]
        value = bin(value)[:1:-1]
        while len(value) < 15:
            value += '0'
        value = value[::-1]
        instruction += value

    # C-instructions:
    elif line[0] is 'C_INSTRUCTION':
        instruction += '111'
        if 'M' in line[2]:
            instruction += '1'
        else:
            instruction += '0'
        instruction += COMPUTATIONS[line[2]]
        instruction += DESTINATIONS[line[1]]
        instruction += JUMPS[line[3]]

    # Invalid input:
    elif DEBUG:
        print '\tInvalid instruction passed to translateLine(): ' + str(line)

    return instruction

#-------------------------------------------------------------------------------
#    Function: isReservedOrIsLabel
#
# Description: Determines whether a given string is a reserved word within the
#              Hack assembly language or was previously defined as a label.
#
#      Inputs: s - A string containing a user-defined label or variable.
#
#     Outputs: 'True' if the string is reserved or is a user-defined label,
#              'False' otherwise.
#-------------------------------------------------------------------------------
def isReservedOrIsLabel(s):
    return s in PREDEFINED_SYMBOLS or s in DESTINATIONS or s in JUMPS or \
           s in LABEL_SYMBOLS

#-------------------------------------------------------------------------------
#    Function: isSymbol
#
# Description: Determines whether a given string could legally serve as a
#              symbol (i.e., a label or variable) within the Hack assembly
#              language. Specifically, the first character must not be a digit
#              and the other characters (if any) must either be letters,
#              digits, or one of the accepted special characters: '_', '.',
#              '$', or ':'. Does not determine whether the given string is a
#              reserved word or previously defined label.
#
#      Inputs: s - A string that may contain a user-defined label or variable.
#
#     Outputs: 'True' if the string satisfies the basic criteria for a Hack
#              assembly language symbol, 'False' otherwise.
#-------------------------------------------------------------------------------
def isSymbol(s):
    if len(s) < 1 or s[0].isdigit():
        return False

    specialChars = '_.$:'
    for i in range(len(s)):
        if not (s[i].isalnum() or s[i] in specialChars):
            return False

    return True

#-------------------------------------------------------------------------------
#    Function: isConstant
#
# Description: Determines whether a given string could legally serve as an
#              integer constant within the Hack assembly language.
#              Specifically, each character must be a digit and the number's
#              value must lie between 0 and 32,767 (inclusive).
#
#      Inputs: s - A string that may contain a user-defined constant.
#
#     Outputs: 'True' if the string satisfies the basic criteria for a Hack
#              assembly language integer constant, 'False' otherwise.
#-------------------------------------------------------------------------------
def isConstant(s):
    if len(s) < 1 or len(s) > 5 or not s.isdigit():
        return False

    n = int(s)
    if 0 <= n <= 32767:
        return True

    return False

#-------------------------------------------------------------------------------
#    Function: fail
#
# Description: Prints an informative error message, then exits the program.
#
#      Inputs: errorMessage     - A string specifying the type of error.
#              sourceLineNum    - Line number (within the source file) where
#                                 the error was encountered.
#              sourceLineString - String containing the code that produced the
#                                 error.
#
#     Outputs: None.
#-------------------------------------------------------------------------------
def fail(errorMessage, sourceLineNum, sourceLineString):
    print 'Error: ' + errorMessage + ' on line ' + str(sourceLineNum)
    print '\t' + sourceLineString
    sys.exit(-1)

#-------------------------------------------------------------------------------
#    Function: main
#
# Description: Processes command line arguments (printing usage information and
#              exiting if any associated error is detected), then handles the
#              parsing and translation of an input file as well as the creation
#              of an output file containing the resulting lines of machine
#              code (assuming no errors were encountered along the way).
#
#      Inputs: An input file must be specified as a command-line argument. It
#              also must already exist and have a '.asm' extension.
#
#     Outputs: None. However, if the program completes successfully, an output
#              file will be created. It will have the same name as the input
#              file, but with a '.hack' extension rather than '.asm'.
#-------------------------------------------------------------------------------
def main():
    # Check for correct number and type of arguments:
    if len(sys.argv) != 2 or \
            (len(sys.argv) > 1 and \
                 sys.argv[1][len(sys.argv[1]) - 4::] != '.asm'):
        print 'Usage: ' + sys.argv[0] + ' [filename].asm'
        return

    # Ensure the file exists and is a valid file:
    inputFilename = sys.argv[1]
    if not os.path.isfile(sys.argv[1]):
        print 'Error: "' + inputFilename + '" does not exist or is not a file.'
        return

    # Read the input (.asm) file:
    fin = open(sys.argv[1], 'r')
    parsedCode = parse(fin)
    fin.close()

    # Write binary instruction strings to the output (.hack) file:
    outputFilename = sys.argv[1][:-len('.asm'):] + '.hack'
    fout = open(outputFilename, 'w')
    processSymbols(parsedCode)
    translatedCode = translate(parsedCode)
    for line in translatedCode:
        print >>fout, line
    fout.close()

if __name__ == '__main__':
    main()
