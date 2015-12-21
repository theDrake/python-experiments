import os, os.path

#------------------------------------------------------------------------------
#    Function: delete_files
#
# Description: Recursively searches a given directory for all files of a given
#              filename and deletes them.
#
#      Inputs: path     - Path of the directory in which to search.
#              filename - Name of the file(s) to be deleted.
#
#     Outputs: Number of files deleted.
#------------------------------------------------------------------------------
def delete_files(path, filename):
    num_files_deleted = 0
    path_list = []
    path_list.append(path)
    for p in path_list:
        if os.path.exists(p):
            #os.chdir(p)
            items = os.listdir(p)
            for i in items:
                if os.path.isdir(i):
                    path_list.append(i)
                elif i.basename == filename:
                    os.remove(i)
                    num_files_deleted += 1

    return num_files_deleted
