class Optional:
    def __init__(self, defaulton=False):
        self.__on = defaulton
    
    def __bool__(self):
        return self.__on
    
    @property
    def on(self):
        return self.__on
    
    @on.setter
    def on(self, status):
        if isinstance(status, int):
            status = (status != 0)

        if not isinstance(status, bool):
            raise TypeError(f'Expected new status to be a bool, but encountered {status}')

        self.__on = status
    
    def enable(self):
        self.__on = True

    def disable(self):
        self.__on = False
    
