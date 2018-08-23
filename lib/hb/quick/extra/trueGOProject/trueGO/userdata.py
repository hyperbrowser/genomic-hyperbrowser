def readUserGoList(Fn):
    with open(Fn) as userfile:
        fileContent = userfile.readlines()
        goTerms = [go_line.strip("\n").split("\t")[0] for go_line in fileContent if
                   go_line.startswith("GO")]
    return goTerms

# if __name__ == "__main__":
    # import os
    # os.chdir('/Users/chakravarthikanduri/Documents/PostDoc_Projs/trueGO_data/')
    # userdata = readUserGoList("user_testdata.txt")
    # print(userdata)