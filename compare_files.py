import difflib

def compare_files(filename1, filename2):
    f = open(filename1, "r")
    filelines1 = f.readlines()
    f.close()
    f = open(filename2, "r")
    filelines2 = f.readlines()
    f.close()
    diffs = difflib.context_diff(filelines1, filelines2, fromfile=filename1,
                                 tofile=filename2)
    count = 0
    for line in diffs:
        print line,
        count += 1
    return count == 0
