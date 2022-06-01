import dis


class ServerVerifier(type):
    def __init__(cls, clsname, bases, clsdict):
        methods = []
        attrs = []

        for func in clsdict:
            try:
                ret = dis.get_instructions(clsdict[func])
            except TypeError:
                pass
            else:
                for i in ret:
                    if i.opname == 'LOAD_GLOBAL':
                        if i.argval not in methods:
                            methods.append(i.argval)
                    elif i.opname == 'LOAD_ATTR':
                        if i.argval not in attrs:
                            attrs.append(i.argval)
        print(methods)
        print(attrs)
        if 'connect' in methods:
            raise TypeError('Cant use connect method!')

        if not ('SOCK_STREAM' in attrs and 'AF_INET' in attrs):
            raise TypeError('Incorrect socket.')
        super().__init__(clsname, bases, clsdict)


class ClientVerifier(type):
    def __init__(cls, clsname, bases, clsdict):
        methods = []
        for func in clsdict:
            try:
                ret = dis.get_instructions(clsdict[func])
            except TypeError:
                pass
            else:
                for i in ret:
                    if i.opname == 'LOAD_GLOBAL':
                        if i.argval not in methods:
                            methods.append(i.argval)
        print(methods)
        for command in ('accept', 'listen', 'socket'):
            if command in methods:
                raise TypeError('Wrong method!')
        super().__init__(clsname, bases, clsdict)

