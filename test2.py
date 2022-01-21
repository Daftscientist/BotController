import inspect

def test(user, message, dm="no"):
    pass

def getDefultArg(func):
    defaultArgs = inspect.getfullargspec(func).defaults
    functionArgs = {'user': [True], 'message': [True], 'dm': [False, 'no']}
    for defultArg in defaultArgs:
        for item in functionArgs:
            try:
                if functionArgs[item][1] == str(defultArg):
                    return defultArg
            except Exception:
                pass

print(getDefultArg(test))