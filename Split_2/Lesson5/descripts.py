class Port:
    def __set__(self, instance, value):
        if not 1024 < value < 65536:
            print('Wrong port!')
            exit(1)
        instance.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        self.name = name
