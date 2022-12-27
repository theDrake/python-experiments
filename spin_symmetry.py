#!usr/bin/python2

def Score(letter1, letter2):
    if letter1 == letter2:
        if SpinSymmetricWithSelf(letter1):
            return 3
        else:
            return 1
    elif SpinSymmetricWithOther(letter1, letter2):
        return 2
    return 0

def SpinSymmetricWithSelf(letter):
    return letter == 'l' or letter == 'x' or letter == 'o'

def SpinSymmetricWithOther(letter1, letter2):
    letters = '' + str(letter1) + str(letter2)
    return (letters.find('b') > -1 and letters.find('q') > -1) or \
           (letters.find('d') > -1 and letters.find('p') > -1) or \
           (letters.find('m') > -1 and letters.find('w') > -1) or \
           (letters.find('n') > -1 and letters.find('u') > -1)

def main():
    fin = open("input.txt", 'r')
    fout = open("output.txt", 'w')
    fileLines = fin.readlines()
    for line in fileLines:
        line = line.strip()
        score = 0
        i = 0
        j = len(line) - 1
        while i <= j:
            score += Score(line[i], line[j])
            i += 1
            j -= 1
        fout.write(line + ' ' + str(score) + '\n')
    fin.close()
    fout.close()

if __name__ == "__main__":
    main()
