class ExitError(Exception):
    def __init__(self,msg="运行错误或参数错误"):
        self.msg = msg

class InputError(Exception):
    def __init__(self,msg="请按照提示输入"):
        self.msg = msg