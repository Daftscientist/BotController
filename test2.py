import inspect

def checkIfOptionalArg(func, argument):
        for arg in str(inspect.signature(func)).split():
            item = arg.replace(",", "").replace(")", "").replace("(", "")
            newitem = item.split("=")[0]
            if newitem == argument:
                if "=" in item:
                    return True
                else:
                    return False
            else:
                pass

def test(one, two, three=None):
    """ hey """
    print(one, two, three)


print(checkIfOptionalArg(test, "two"))