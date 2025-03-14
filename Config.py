import yaml

class Config:
    def __init__(self):
        with open("./config/config.yml", encoding='utf-8') as f:
            data = yaml.load(f.read(), Loader=yaml.FullLoader)

        self.qrcodeLogin = data["qrcodeLogin"]
        self.priceView = data["priceView"]
        self.debug = data["debug"]
        self.userName = data["userName"]
        self.userPassword = data["userPassword"]