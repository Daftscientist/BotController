class CheckerFunction(object):
    def __init__(self, function, **defaults):
        self.function = function
        self.defaults = defaults

    def __call__(self, **kwargs):
        for key in self.defaults:
            if(key in kwargs):
                if(kwargs[key] == self.defaults[key]):
                    print('passed default')
                else:
                    print('passed different')
            else:
                print('not passed')
                kwargs[key] = self.defaults[key]

        return self.function(**kwargs)

def f(a):
    print(a)

check_f = CheckerFunction(f, a='z')
check_f(a='z')
check_f(a='b')
check_f()