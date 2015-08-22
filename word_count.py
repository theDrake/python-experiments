#!usr/bin/python2

def NumberOfWordsInFile(filename):
    f = open(filename, 'r')
    fileLines = f.readlines()
    f.close()
    wordCount = 0
    for line in fileLines:
        if line == '\xef\xbb\xbf':  # Check for EOF
            break
        line = line.split()
        wordCount += len(line)
    return wordCount

def main():
    words = NumberOfWordsInFile("input.txt")
    fout = open("output.txt", 'w')
    fout.write(str(words) + '\n')
    fout.close()

if __name__ == "__main__":
    main()
