#!/usr/bin/env python

# Single quotes and double quotes:
print('\'hello\'')
print('"hello"')
print("\"hello\"")
print("'hello'")
print("""In this string, I can use ' and " without a '\\'!""")
print('''Same 'with' "this" string!''')

# Variables:
balance = 1446.509
print(balance)
print(str(balance))
print('Remaining balance: $%.2f' % balance)
name = input('What is your name? ')
print(name)
print(name.upper())
print(name.lower())
print('Your name is ' + str(len(name)) + ' letters long.')
description = 'awesome'
print('You are totally %s!!!' % description)
