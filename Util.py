import json

import Error
import execjs

class Util:
    def __init__(self):
        with open("./js/SM4.js",encoding="utf-8") as sm4:
            sm4Code = sm4.read()
        with open("./cityCode/cityCode.json",encoding="utf-8") as cityF:
            cityJson = json.loads(cityF.read())
        self.sm4 = execjs.compile(sm4Code)
        self.cityJson = cityJson
        self.SM4_key = "tiekeyuankp12306"

    # 统一处理用户输入
    def userInput(self, msg, returnType):
        context = input(msg + "\n")
        try:
            return returnType(context)
        except:
            raise Error.InputError()

    # 根据city名字获取city代码
    def getCityCode(self,cityName):
        return self.cityJson.get(cityName, None)

    # 根据city代码获取city名字
    def getCityName(self,cityCode):
        if (cityCode in self.cityJson.values()):
            for key, value in self.cityJson.items():
                if value == cityCode:
                    return key
        else:
            return None

    # 将原始车次数据解析
    def getTimeInterval(self,startTime, endTime):
        cY = startTime.replace(":", "")
        cX = endTime.replace(":", "")
        hour_value = int(cY[0:2]) + int(cX[0:2])
        min_value = int(cY[2:4]) + int(cX[2:4])
        if min_value >= 60:
            hour_value = hour_value + 1
        if 24 <= hour_value < 48:
            return "次日"
        elif 48 <= hour_value < 72:
            return "两日"
        elif hour_value >= 72:
            return "三日"
        else:
            return "当日"

    # 将席位代码转为中文
    def dealSeatType(self,priceData,seatTypes) ->list:

        data = priceData['data']

        if seatTypes == '1341':
            soft_sleep_price = data['A4']
            hard_sleep_price = data['A3']
            hart_seat_price = data['A1']
            no_seat_price = data['WZ']
            return self.dealSeatTypeResult(soft_sleep_price=["4",soft_sleep_price,"软卧"],
                          hard_sleep_price=["3",hard_sleep_price,"硬卧"],
                          hard_seat_price=["1",hart_seat_price,"硬座"],
                          no_seat_price=["1",no_seat_price,"无座"])

        # if seatTypes == '131':
        #     high_soft_sleep_price = data['A6']
        #     soft_sleep_price = data['A4']
        #     hard_sleep_price = data['A3']
        #     hard_seat_price = data['A1']
        #     return result(high_soft_sleep_price=["A6", high_soft_sleep_price, "高级软卧"],
        #                   soft_sleep_price=["A4", soft_sleep_price, "软卧"],
        #                   hard_sleep_price=["A3", hard_sleep_price, "硬卧"],
        #                   hard_seat_price=["A1", hard_seat_price, "硬座"])

        if seatTypes == '131':
            hard_sleep_price = data['A3']
            hard_seat_price = data['A1']
            no_seat_price = data['WZ']
            return self.dealSeatTypeResult(hard_sleep_price=["3", hard_sleep_price, "硬卧"],
                          hard_seat_price=["1", hard_seat_price, "硬座"],
                          no_seat_price=["1",no_seat_price,"无座"])

        if seatTypes == '1346':
            soft_sleep_price = data['A4']
            hard_sleep_price = data['A3']
            hard_seat_price = data['A1']
            return self.dealSeatTypeResult(soft_sleep_price=["4", soft_sleep_price, "软卧"],
                          hard_sleep_price=["3", hard_sleep_price, "硬卧"],
                          hard_seat_price=["1", hard_seat_price, "硬座"])

        if seatTypes == '134':
            soft_sleep_price = data['A4']
            hard_sleep_price = data['A3']
            hard_seat_price = data['A1']
            return self.dealSeatTypeResult(soft_sleep_price=["4", soft_sleep_price, "软卧"],
                          hard_sleep_price=["3", hard_sleep_price, "硬卧"],
                          hard_seat_price=["1", hard_seat_price, "硬座"])

        if seatTypes == '9MO' or seatTypes == 'OM9':
            special_price = data['A9']
            first_seat_price = data['M']
            second_seat_price = data['O']
            return self.dealSeatTypeResult(special_price=["9", special_price, "商务座/特等座"],
                          first_seat_price=["M", first_seat_price, "一等座"],
                          second_seat_price=["O", second_seat_price, "二等座"])

        if seatTypes == 'MOO':
            first_seat_price = data['M']
            second_seat_price = data['O']
            return self.dealSeatTypeResult(first_seat_price=["M", first_seat_price, "一等座"],
                          second_seat_price=["O", second_seat_price, "二等座"])

        if seatTypes == 'FOO':
            dong_sleep_price = data['F']
            second_seat_price = data['O']
            no_seat_price = data['O']
            return self.dealSeatTypeResult(dong_sleep_price=["F", dong_sleep_price, "动卧"],
                          second_seat_price=["O", second_seat_price, "二等座"],
                          no_seat_price=["O", no_seat_price, "无座"])

        if seatTypes == 'FO':
            dong_sleep_price = data['F']
            second_seat_price = data['O']
            return self.dealSeatTypeResult(dong_sleep_price=["F", dong_sleep_price, "动卧"],
                          second_seat_price=["O", second_seat_price, "二等座"])

        if seatTypes == 'F':
            dong_sleep_price = data['F']
            return self.dealSeatTypeResult(dong_sleep_price=["F", dong_sleep_price, "动卧"])

        if seatTypes == 'MOP':
            special_price = data['P']
            second_seat_price = data['O']
            first_seat_price = data['M']
            return self.dealSeatTypeResult(special_price=["P", special_price, "商务座/特等座"],
                          second_seat_price=["O", second_seat_price, "二等座"],
                          first_seat_price=["M", first_seat_price, "一等座"])

        if seatTypes == 'IJO':
            soft_sleep_price = data['AI']
            second_seat_price = data['O']
            hard_sleep_price = data['AJ']
            return self.dealSeatTypeResult(soft_sleep_price=["I", soft_sleep_price, "软卧"],
                          second_seat_price=["O", second_seat_price, "二等座"],
                          hard_sleep_price=["J", hard_sleep_price, "硬卧"])

        return self.dealSeatTypeResult()

    # 统一处理席位代码转中文
    def dealSeatTypeResult(self,special_price=None, first_seat_price=None, second_seat_price=None, high_soft_sleep_price=None,soft_sleep_price=None, dong_sleep_price=None, hard_sleep_price=None, soft_seat_price=None,hard_seat_price=None,no_seat_price=None) -> list:
        if not soft_seat_price:
            soft_seat_price = ["未更新", "未更新", "未更新"]
        args = locals()
        args.pop("self")
        data = []
        for key, value in args.items():
            if (value):
                data.append({"seatType": value[0], "price": value[1], "seatName": value[2]})
            else:
                data.append({})
        return data

    # ecb加密
    def encrypt_ecb(self,data):
        return self.sm4.call("encrypt_ecb", data,self.SM4_key)

    # ecb解密
    def decrypt(self, data):
        return self.sm4.call("decrypt_cbc", data, self.SM4_key)
