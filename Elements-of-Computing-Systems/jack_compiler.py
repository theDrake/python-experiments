#!usr/bin/python2

#-------------------------------------------------------------------------------
#    Filename: jack_compiler.py
#
#     Authors: David C. Drake (https://davidcdrake.com) and Thomas Gull
#
# Description: Classes and functions for compiling Jack code into VM code
#              according to the specifications outlined in "The Elements of
#              Computing Systems," by Nisan and Schocken (MIT Press, 2005).
#              Developed using Python 2.7.
#-------------------------------------------------------------------------------

import sys
import os

global current_line_num
global num_whiles
global num_ifs

keywords = ['class', 'constructor', 'function', 'method', 'field', 'static',
            'var', 'int', 'char', 'boolean', 'void', 'true', 'false', 'null',
            'this', 'let', 'do', 'if', 'else', 'while', 'while', 'return']
symbols = ['{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/',
           '&', '|', '<', '>', '=', '~']

TOKENS = 'T.xml'
XML = '.xml'
VM = '.vm'
OUTPUT_TYPE = VM
NUM_KINDS = 4
STATIC, FIELD, ARG, VAR = range(NUM_KINDS)
NUM_SCOPES = 2
CLASS, SUBROUTINE = range(NUM_SCOPES)

class Symbol:
    def __init__(self, name, type, kind, index):
        self.name = name
        self.type = type
        self.kind = kind
        self.index = index

class SymbolTable:
    def __init__(self):
        self.classSymbols = {}
        self.subroutineSymbols = {}
        self.index = []
        for i in range(NUM_KINDS):
            self.index.append(0)

    def startSubroutine(self):
        self.subroutineSymbols = []
        self.index[ARG] = 0
        self.index[VAR] = 0

    def define(self, name, type, kind):
        if kind in [STATIC, FIELD]:
            self.classSymbols.append(Symbol(name,
                                            type,
                                            kind,
                                            self.index[kind]))
        else:
            self.subroutineSymbols.append(Symbol(name,
                                                 type,
                                                 kind,
                                                 self.index[kind]))
        self.index[kind] += 1

    def varCount(self, kind):
        return self.index[kind]

    def kindOf(self, name):
        s = self.retrieve(name)
        if s:
            return s.kind
        return None

    def typeOf(self, name):
        s = self.retrieve(name)
        if s:
            return s.type
        return None

    def indexOf(self, name):
        s = self.retrieve(name)
        if s:
            return s.index
        return None

    def retrieve(self, name):
        if name in self.subroutineSymbols:
            return self.subroutineSymbols[name]
        if name in self.classSymbols:
            return self.classSymbols[name]
        return None

class JackTokenizer:
    def __init__(self, file_name):
        self.token_file = file_name
        fin = open(file_name, 'r')
        self.token_string = fin.read().replace('\r\n', '\n').replace('\r', '\n')
        fin.close()
        self.i = 0
        self.line_number = 1

    def getToken(self):
        self.i = 0

        if self.token_string == '\n':
            return None

        while self.i < len(self.token_string):

            # Skip whitespace:
            if self.token_string[self.i].isspace():
                while self.token_string[self.i].isspace():
                    if self.token_string[self.i] == '\n':
                        self.line_number += 1
                    self.i += 1
                self.token_string = self.token_string[self.i:]
                self.i = 0
                continue

            # Skip single-line comments:
            if self.token_string[self.i:self.i + 2] == '//':
                while self.token_string[self.i] != '\n':
                    self.i += 1
                self.token_string = self.token_string[self.i:]
                self.i = 0
                continue

            # Skip block comments:
            if self.token_string[self.i:self.i + 2] == '/*':
                while self.token_string[self.i:self.i + 2] != '*/':
                    if self.token_string[self.i] == '\n':
                        self.line_number += 1
                    self.i += 1
                self.token_string = self.token_string[self.i + 2:]
                self.i = 0
                continue

            # Check for a symbol:
            if self.token_string[self.i] in symbols:
                return_symbol = self.token_string[self.i]
                self.token_string = self.token_string[self.i + 1:]
                return ('symbol', return_symbol, self.line_number)

            # Check for an integer constant:
            if self.token_string[self.i].isdigit():
                while self.token_string[self.i].isdigit():
                    self.i += 1
                mydigit = int(self.token_string[:self.i])
                if not integerConstant(mydigit):
                    fail('Integer constants must be within the range 0 to ' + \
                         '32767 (inclusive).',
                         self.token_file,
                         self.line_number)
                self.token_string = self.token_string[self.i:]
                return ('integerConstant', mydigit, self.line_number)

            # Check for a string constant:
            if self.token_string[self.i] == '"':
                while self.token_string[self.i + 1] is not '"':
                    if self.token_string[self.i] == '\n':
                        fail('String constants may not include "\n".',
                             self.token_file,
                             self.line_number)
                    self.i += 1
                mystring = self.token_string[1:self.i + 1]
                self.token_string = self.token_string[self.i + 2:]
                return ('stringConstant', mystring, self.line_number)

            # Check for an identifier or keyword:
            if self.token_string[self.i].isalnum() or \
               self.token_string[self.i] == '_':
                while self.token_string[self.i].isalnum() or \
                      self.token_string[self.i] == '_':
                    self.i += 1
                myidentifier = self.token_string[:self.i]
                self.token_string = self.token_string[self.i:]
                if myidentifier in keywords:
                    return ('keyword', myidentifier, self.line_number)
                else:
                    return ('identifier', myidentifier, self.line_number)

            # Anything else at this point is an error:
            else:
                fail('Invalid syntax.', self.token_file, self.line_number)

        return None

class CompilationEngine:
    def __init__(self, token_list, input_file, output_file):
        global current_line_num
        self.input_file = input_file
        self.token_list = token_list
        self.out = open(output_file, 'w') #output_file
        #print >>self.out, "<tokens>"
        self.indent = 0  # No. of spaces to print before lines of output.
        self.i = 0  # Index of the current token.
        current_line_num = -1 # To be updated as tokens are read.

    def tokenFile(self):
        print >>self.out, "<tokens>"

    def closeTokens(self):
        print >>self.out, "</tokens>"
        self.out.close()

    def close(self):
        self.out.close()

    def nextToken(self):
        global current_line_num
        t = self.token_list[self.i]
        self.i += 1
        if t:
            current_line_num = t[2]
        return t

    def peek(self):
        global current_line_num
        if self.i >= len(self.token_list):
            return None
        t = self.token_list[self.i]
        if t:
            current_line_num = t[2]
            return t
        return None

    def write(self, s):
        print >>self.out, ' ' * self.indent + str(s)

    def writeTag(self, token): #tag, content):
        tag = str(token[0])
        content = str(token[1])
        if content == '<':
             content = '&lt;'
        elif content == '>':
            content = '&gt;'
        elif content == '&':
            content = '&amp;'
        self.write('<' + tag + '> ' + content + ' </' + tag + '>')
        #self.write('<' + str(tag) + '>')
        #self.indent += 2
        #self.write(str(content))
        #self.indent -= 2
        #self.write('</' + str(tag) + '>')

    def writeOut(self, token):
        tag = str(token[0])
        content = str(token[1])
        if content == '<':
             content = '&lt;'
        elif content == '>':
            content = '&gt;'
        elif content == '&':
            content = '&amp;'
        self.write('<' + tag + '> ' + content + ' </' + tag + '>')

    def keyword(self, kw):
        global current_line_num

        t = self.nextToken()
        if t[0] == 'keyword' and t[1] == kw:
            self.writeTag(t)
        elif t:
            fail('Expected "' + str(kw) + '", found "' + str(t[0]) + '".',
                 self.input_file,
                 t[2])
        else:
            fail('Expected "' + kw + '", found nothing.',
                 self.input_file,
                 current_line_num)

        return kw

    def identifier(self): #, identifier):
        global current_line_num

        t = self.nextToken()
        if t[0] == 'identifier':# and t[1] == identifier:
            self.writeTag(t)
        elif t:
            fail('Expected identifier and instead found "' + t[1] + \
                 '".',
                 self.input_file,
                 t[2])
        else:
            fail('Expected identifier and instead found nothing.',
                 '',
                 current_line_num)

        return t

    def symbol(self, symbol):
        global current_line_num

        t = self.nextToken()
        #if t and t[1] == symbol:
        if t[0] == 'symbol' and t[1] == symbol:
            #write_out = '<symbol>'
            self.writeTag((t[0], t[1], t[2]))
            #self.write('<symbol>')
            #self.indent += 2
            #self.write(symbol)
            #self.indent -= 2
            #self.write('</symbol>')
        elif t:
            fail('Expected symbol "' + symbol + '", found "' + t[1] + '".',
                 self.input_file,
                 t[2])
        else:
            fail('Expected symbol "' + symbol + '", found nothing.',
                 self.input_file,
                 current_line_num)

        return t

    def expectType(self):
        t = self.peek()
        print t[0]
        if t[1] in ['int', 'char', 'boolean']:
            return self.keyword(t[1])
        elif t:
            return self.identifier()

        return None

    def compileClass(self):
        global current_line_num

        self.write('<class>')
        self.indent += 2
        self.keyword('class')
        self.identifier()
        self.symbol('{')

        while True:
            t = self.peek()
            if t[1] in ['static', 'field']:
                self.compileClassVarDec()
            else:
                break

        while True:
            t = self.peek()
            if t[1] in ['constructor', 'function', 'method']:
                self.compileSubroutine()
            else:
                break

        self.symbol('}')
        self.indent -= 2
        self.write('</class>')

    def compileClassVarDec(self):
        self.write('<classVarDec>')
        self.indent += 2
        self.writeTag(self.nextToken())
        self.expectType()
        self.expectType()
        while self.peek()[1] != ';':
            self.symbol(',')
            self.expectType()
        self.symbol(';')
        self.indent -= 2
        self.write('</classVarDec>')

    def compileSubroutine(self):
        self.write('<subroutineDec>')
        self.indent += 2
        self.keyword(self.peek()[1])
        print self.peek()
        if self.peek()[0] == 'keyword':
            self.keyword(self.peek()[1])
        self.identifier()
        if self.peek()[0] == 'identifier':
            self.identifier()
        self.symbol('(')
        self.write('<parameterList>')
        self.indent += 2
        self.parameterList()
        self.indent -= 2
        self.write('</parameterList>')
        self.symbol(')')

        self.write('<subroutineBody>')
        self.indent += 2
        self.symbol('{')
        while self.peek()[1] == 'var':
            self.write('<varDec>')
            self.indent += 2
            self.keyword('var')
            self.expectType()
            self.identifier()
            while self.peek()[1] != ';':
                self.symbol(',')
                self.identifier()
            self.symbol(';')
            self.indent -= 2
            self.write('</varDec>')

        while self.peek()[1] != '}':
            self.writeStatement()
        self.symbol('}')
        self.indent -= 2
        self.write('</subroutineBody>')

        self.indent -= 2
        self.write('</subroutineDec>')

    def parameterList(self):
        if self.peek()[1] != ')':
            self.expectType()
            self.identifier()
            while self.peek()[1] != ')':
                self.symbol(',')
                self.expectType()
                self.identifier()
            #self.symbol(')')

    def writeStatement(self):
        self.write('<statements>')
        self.indent += 2
        while self.peek()[1] != '}':
            self.statements()
        #self.symbol('}')
        self.indent -= 2
        self.write('</statements>')
        #self.symbol('}')

    def statements(self):
        if self.peek()[1] == 'let':
            self.letStatement()
        elif self.peek()[1] == 'if':
            self.ifStatement()
        elif self.peek()[1] == 'while':
            self.whileStatement()
        elif self.peek()[1] == 'do':
            self.doStatement()
        elif self.peek()[1] == 'return':
            self.returnStatement()

    def letStatement(self):
        self.write("<letStatement>")
        self.indent += 2
        self.keyword('let')
        self.identifier()
        if self.peek()[1] == '[':
            self.symbol('[')
            self.expression()
            self.symbol(']')
        self.symbol('=')
        self.expression()
        self.symbol(';')
        self.indent -= 2
        self.write("</letStatement>")

    def ifStatement(self):
        self.write("<ifStatement>")
        self.indent += 2
        self.keyword('if')
        self.symbol('(')
        while self.peek()[1] != ')':
            self.expression()
        self.symbol(')')
        self.symbol('{')
        while self.peek()[1] != '}':
            self.writeStatement()
        self.symbol('}')
        self.indent -= 2
        self.write("</ifStatement>")

    def whileStatement(self):
        self.write("<whileStatement>")
        self.indent += 2
        self.keyword('while')
        self.symbol('(')
        self.expression()
        self.symbol(')')
        self.symbol('{')
        self.writeStatement()
        self.symbol('}')
        self.indent -= 2
        self.write("</whileStatement>")

    def doStatement(self):
        self.write("<doStatement>")
        self.indent += 2
        self.keyword('do')
        self.identifier()
        self.subroutineCall()
        self.symbol(';')
        self.indent -= 2
        self.write("</doStatement>")

    def returnStatement(self):
        self.write("<returnStatement>")
        self.indent += 2
        self.keyword('return')
        if str(self.peek()[1]) != ';':
            self.expression()
        self.symbol(';')
        self.indent -= 2
        self.write("</returnStatement>")

    def expression(self):
        self.write("<expression>")
        self.indent += 2
        while str(self.peek()[1]) not in ');],':
            self.term()
            if self.peek()[0] == 'symbol' and self.peek()[1] in '=<>+-/':
                self.symbol(self.peek()[1])
        #self.symbol(self.peek()[1])
        self.indent -= 2
        self.write("</expression>")

    def term(self):
        self.write("<term>")
        self.indent += 2
        #while str(self.peek()[1]) not in ');]':
        term = self.peek()[0]
        if term == 'integerConstant' or term == 'stringConstant' \
            or term == 'keyword':
            self.writeTag(self.nextToken())
        elif term == 'identifier':
            self.identifier()
            if self.peek()[0] == 'symbol' and (self.peek()[1] == '.' or self.peek()[1] == '('):
                self.subroutineCall()
            elif self.peek()[0] == 'symbol' and self.peek()[1] == '[':
                self.symbol('[')
                self.expression()
                self.symbol(']')
        elif term == 'symbol' and self.peek()[1] == '(':
            self.expression()
            self.symbol(')')
        elif term in '-~' and self.peek()[0] == 'symbol':
            self.symbol(term)
        else:
            fail('Invalid term found.', self.input_file, self.peek()[2])
        #symbol, op = self.peek()[0], self.peek()[1]
        #if symbol == 'symbol' and op in ');]':
        #    break
        #if symbol == 'symbol' and op in '+-*/&|<>=':
        #    self.symbol(op)
        #    self.term()
        #else:
        #    fail('Invalid term found.', self.input_file, self.peek()[2])
        self.indent -= 2
        self.write("</term>")

    def subroutineCall(self):
        if self.peek()[1] == '.':
            self.symbol('.')
            self.identifier()
        self.symbol('(')
        self.write("<expressionList>")
        self.indent += 2
        if self.peek()[1] != ')':
            self.expression()
            while self.peek()[1] == ',':
                self.symbol(',')
                self.expression()
        self.indent -= 2
        self.write("</expressionList>")
        self.symbol(')')
        # elif self.peek()[1] == '(':
            # self.symbol('(')
            # self.expression()
            # self.symbol(')')
        # else:
            # fail("Erroneous subroutine call.", self.input_file, self.peek()[2])

#-------------------------------------------------------------------------------
#    Function: integerConstant
#
# Description: Determines whether a given integer is a valid Jack integer
#              constant (i.e., whether it is within the range 0-32767,
#              inclusive).
#
#      Inputs: integer - The value to be tested.
#
#     Outputs: 'True' if the integer is valid, 'False' otherwise.
#-------------------------------------------------------------------------------
def integerConstant(integer):
    return integer >= 0 and integer <= 32767

#-------------------------------------------------------------------------------
#    Function: fail
#
# Description: Prints an error message, along with the line of code that
#              produced the error and its line number, then exits.
#
#      Inputs: error_msg   - A message describing the error encountered.
#              source      - The name of the file which produced the error.
#              line_number - The line number where the error occurred.
#
#     Outputs: None.
#-------------------------------------------------------------------------------
def fail(error_msg, source, line_number):
    print >>sys.stderr, 'Error on line %d: %s' % (line_number, error_msg)
    print >>sys.stderr, '\t%s' % source
    sys.exit(-1)

#-------------------------------------------------------------------------------
#    Function: main
#
# Description: Validates command line input, then
#
#      Inputs: sys.argc - The name of a Jack file, or of a directory containing
#                         one or more Jack files, must be provided as a command
#                         line argument.
#
#     Outputs: None. However, one or more VM output files is created.
#-------------------------------------------------------------------------------
def main():
    output_files = {}
    if len(sys.argv) != 2:
        print >>sys.stderr, 'You must provide a filename or directory.'
        sys.exit(-1)

    # enable user to name program 'token.py'
    # if so then we output .xml file with
    # list of tokens.
    # The difference between TOKENS and XML is:
    # TOKENS outputs just a list of tokens,
    # and XML will output jack structure, i.e. class and keywords, symbols etc.
    basename = os.path.basename(sys.argv[0])
    if basename == 'token.py':
        OUTPUT_TYPE = TOKENS
    else:
        OUTPUT_TYPE = XML

    # We need to determine if the file input is a directory or single file,
    # do some error checking and then create two lists:
    # one containing list of input files and their associated output files.
    # each index of the input file list will also be its respectful output file index
    full_path = os.path.abspath(sys.argv[1])
    files_list = []
    if full_path.endswith('.jack'):
        # make sure the input file exists first.
        if os.path.isfile(full_path):
            output_files[full_path] = full_path[:-len('.jack')] + OUTPUT_TYPE # '.xml' or '.vm' ?
        else:
            print >>sys.stderr, 'File "%s" does not exist.' % full_path
            sys.exit(-1)
        files_list.append(full_path)
    else:
        # make sure the input directory exists.
        if not os.path.isdir(full_path):
            print >>sys.stderr, 'Directory "%s" does not exist.' % full_path
        list_files = os.listdir(full_path)
        for each in list_files:
            if each.endswith('.jack'):
                tmp = os.path.join(full_path, each)
                files_list.append(tmp)
                if os.path.isfile(tmp):
                    output_files[tmp] = tmp[:-len('.jack')] + OUTPUT_TYPE # '.xml' or '.vm' ?

    # gather up all the tokens into a list
    # This will be a list of lists, each sublist
    # will be a token list of the file and its
    # index will associate with both its input and output files.
    all_tokens = []
    for each in files_list:
        file_token = JackTokenizer(each)
        token_list = []
        while True:
            new_token = file_token.getToken()
            if new_token == None:
                break
            else:
                token_list.append(new_token)
        all_tokens.append(token_list)
    # if our program is named token.py then we output tokens to .xml file
    if OUTPUT_TYPE == TOKENS:
        for i in range(len(all_tokens)):
            tokenizer = CompilationEngine(all_tokens[i],
                                          files_list[i],
                                          output_files[files_list[i]])
            tokenizer.tokenFile()
            while (tokenizer.peek()):
                tokenizer.writeTag(tokenizer.nextToken())
            tokenizer.closeTokens()
    elif OUTPUT_TYPE == XML:
        for i in range(len(all_tokens)):
            xml = CompilationEngine(all_tokens[i],
                                    files_list[i],
                                    output_files[files_list[i]])
            xml.compileClass()
            xml.close()

if __name__ == '__main__':
    main()
