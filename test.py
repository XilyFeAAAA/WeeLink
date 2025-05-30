class Log:
    pass


class BaseMixIn:
    pass


class MsgMixIn(BaseMixIn):
    def get(self):
        print(self.log)
        
class Bot(MsgMixIn):
    
    
    def __init__(self) -> None:
        super().__init__()
        self.log = Log()
        
    def get_2(self):
        print(self.log)
        
bot = Bot()
bot.get()
bot.get_2()