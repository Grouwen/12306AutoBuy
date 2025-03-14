import base64
import datetime
import os
import Logger
import random
import time
import Error
from pyzbar.pyzbar import decode
from PIL import Image
import Bot
import Config
import qrcode
import Util
import json
import prettytable as pt
import re
import Api


# 登录12306
def login():
    # 判断能否自动登录
    if os.path.exists("./cookie/cookie.json"):
        print("您已登录过一次，将检测能否自动登录")
        try:
            # 添加cookie
            with open("./cookie/cookie.json","r") as f:
                cookie = json.loads(f.read())
            bot.baseReq.utils.add_dict_to_cookiejar(bot.req.cookies, cookie)

            # 检测是否登录
            if isLogin():
                print("登录成功")
                return
        except json.JSONDecodeError:
            print("cookie文件已损坏，将重新登录")

    # 登录12306
    if config.qrcodeLogin:
        # 扫码登陆

        # 获取base64的图片
        qrcodeJson = bot.postJson(api.LOGIN_BY_QR_CODE, data={"appid": "otn"})["data"]
        imgdata = base64.b64decode(qrcodeJson["image"])
        with open("12306QrCode.jpg", 'wb') as f:
            f.write(imgdata)

        # 将图片打印到控制台
        barcode_url = ""
        barcodes = decode(Image.open('./12306QrCode.jpg'))
        for barcode in barcodes:
            barcode_url = barcode.data.decode("utf-8")
        qr = qrcode.QRCode()
        qr.add_data(barcode_url)

        # 终端打印二维码
        qr.print_ascii(invert=True)
        print("请尽快扫描上方二维码！如扫描不上，可以离远扫描或者打开12306QrCode.jpg，位置在" + os.path.abspath(
            os.curdir) + "\\" + "12306QrCode.jpg")

        # 轮询，查询当前状态
        while True:
            data = {
                "uuid": qrcodeJson["uuid"],
                "appid": "otn"
            }
            checkqrJson = bot.postJson(api.LOGIN_BY_QR_CODE_CHECK, data=data)["data"]
            # 0：未识别、
            # 1：已识别，暂未授权（未点击授权或不授权）、
            # 2：登录成功，（已识别且已授权）、
            # 3：已失效、
            # 5 系统异常
            checkqrCode = checkqrJson["result_code"]
            if (checkqrCode == "1"):
                print("已扫描，请尽快确认")
            elif (checkqrCode == "3"):
                raise Error.ExitError("二维码已失效")
            elif (checkqrCode == "2"):
                break

            time.sleep(1.5)
    else:
        # 账号密码登录
        # 检测账号的登录验证模式
        if not (config.userName or config.userPassword):
            raise Error.ExitError("账号或密码为空，请前往修改config.yml文件")

        password = "@" + util.encrypt_ecb(config.userPassword)
        data = {
            "sessionId": "",
            "sig": "",
            "if_check_slide_passcode_token": "",
            "scene": "",
            "checkMode": 0,
            "randCode": "",
            "username": config.userName,
            "password": password,
            "appid": "otn"
        }

        checkLoginVerifyData = {
            "username":config.userName,
            "appid":"otn"
        }
        loginMod = bot.postJson(api.LOGIN_CHECK_VERIFY,data=checkLoginVerifyData)["data"]
        mod = loginMod["login_check_code"]
        if mod == "1":
            raise Error.ExitError("未制作的登录验证方式：1")
        elif mod == "2":
            raise Error.ExitError("未制作的登录验证方式：2")
        elif mod == "3":
            randCode = loginMod3()
            data["randCode"] = randCode

        # 验证完后，发起登录api
        loginCodeJson = bot.postJson(api.LOGIN_URL, data=data)["data"]
        if loginCodeJson["result_code"] != 0:
            raise Error.ExitError(loginCodeJson["result_message"])

    # 初始化12306
    uamtkJson = bot.postJson(api.INIT_UAMTK, data={"appid": "otn"})["data"]

    bot.postJson(api.INIT_UAMTK_CLIENT, data={"tk": uamtkJson["newapptk"]})

    if isLogin():
        name = bot.postJson(api.INIT_12306)["data"]
        print(name["data"]["user_name"] + "，登录成功")
        with open("./cookie/cookie.json", "w") as f:
            f.write(json.dumps(bot.req.cookies.get_dict()))
        print("已将cookie信息保存，下次将自动登录")
    else:
        print("登录失败！")
        raise Error.ExitError("登录时遇到未知原因")

# 登录模式3，需要验证码登录
def loginMod3():
    # 登录验证模式3，需要验证码登录
    print("您的账号需要短信验证")
    castNum = util.userInput("请输入登录账号绑定的证件号后4位", int)
    data = {
        "appid":"otn",
        "username":config.userName,
        "castNum":castNum
    }
    messageJson = bot.postJson(api.LOGIN_BY_MESSAGECODE, data=data)["data"]

    # 判断是否成功获取验证码
    if messageJson["result_code"] != 0:
        raise Error.ExitError(messageJson["result_message"])
    randCode = util.userInput(messageJson["result_message"], str)
    return randCode


# 检测是否登录
def isLogin()->bool:
    conf = bot.postJson(api.LOGIN_CONFIM,data={"_json_att": ""})["data"]
    if (conf["data"]["is_login"] == "Y"):
        return True
    else:
        return False

# 获取所有列车信息并打印
def getTrainInfo(trainDate:str,fromStation:str,toStation:str)->list:
    # 获取列车信息
    trainParam = {
        "leftTicketDTO.train_date": trainDate,
        "leftTicketDTO.from_station": fromStation,
        "leftTicketDTO.to_station": toStation,
        "purpose_codes": "ADULT"
    }
    trainInfo = bot.getJson(api.QUERY_LEFT_TICKET, params=trainParam)
    trainJson = trainInfo["data"]

    # 将获取的数据格式化输出
    trains = []
    num = 0
    tb = pt.PrettyTable()

    tb.field_names = ['序号', '车次', '出发站', '到达站', '开始时', '结束时', '何时到达', '历时',
                      '商务座/特等座', '一等座', '二等座', '高级软卧', '软卧', '动卧', '硬卧', '软座', '硬座', '无座',
                      '状态']
    trainResult = list(trainJson["data"]["result"])
    for trainData in trainResult:
        print("正在获取第", num + 1, "/", len(trainResult), "个车次的信息")
        t = trainData.split("|")
        trainNo = t[2]
        che = t[3]
        startcode = util.getCityName(t[6])
        endcode = util.getCityName(t[7])
        if (t[7] != t[5]):
            endcode += "（过）"

        starttime = t[8]
        endtime = t[9]
        duration_time = t[10]
        fromStationCode = t[16]
        toStationCode = t[17]
        arriveDate = util.getTimeInterval(starttime, duration_time)
        special_seat = t[32] or t[25] or '--'

        first_seat = t[31] or '--'
        second_seat = t[30] or '--'
        high_sleep = t[21] or '--'
        soft_sleep = t[23] or '--'
        dong_sleep = t[33] or '--'
        hard_sleep = t[28] or '--'
        soft_seat = t[24] or '--'
        hart_seat = t[29] or '--'
        no_seat = t[26] or '--'
        seatType = t[35]

        if (t[11] == "Y"):
            status = t[1]
        elif (t[11] == "IS_TIME_NOT_BUY"):
            status = t[1]
        else:
            status = "--"

        # 如果用户开启priceView，则调用getSeatPrice
        if (config.priceView):
            prices = getSeatPrice(trainNo, fromStationCode, toStationCode, seatType, trainDate)
            mapToSeat = [special_seat, first_seat, second_seat, high_sleep, soft_sleep, dong_sleep, hard_sleep,
                         soft_seat, hart_seat, no_seat]
            for index in range(0, len(prices)):
                if (prices[index] and mapToSeat[index] != "--" and mapToSeat[index] != "无"):
                    mapToSeat[index] += "/" + prices[index]["price"]

            rowData = [num + 1, che, startcode, endcode, starttime, endtime, arriveDate, duration_time]
            for seat in mapToSeat:
                rowData.append(seat)
            rowData.append(status)
        else:
            rowData = [num + 1, che, startcode, endcode, starttime, endtime, arriveDate, duration_time,
                       special_seat, first_seat, second_seat, high_sleep, soft_sleep, dong_sleep, hard_sleep, soft_seat,
                       hart_seat, no_seat,
                       status]

        tb.add_row(rowData)

        trains.append({
            "no":num+1,
            "secretStr": bot.baseReq.utils.unquote(t[0]),
            "trainDate": trainDate,
            "startcode": startcode,
            "endcode": endcode,
            "trainNo": trainNo,
            "fromStationCode": fromStationCode,
            "toStationCode": toStationCode,
            "seatType": seatType,
            "leftTicket": t[12],
            "trainLocation": t[15],
            "stationTrainCode": t[3],
            "fromStationTelecode": t[6],
            "toStationTelecode": t[7]
        })
        num += 1

        if (config.priceView):
            time.sleep(random.randint(2, 5))

    print(tb)
    return trains

# 获取席位价格
def getSeatPrice(trainNo, fromStationNo, toStationNo, seatTypes, trainDate):

    # 发送请求，获取席位价格
    params = {
        "train_no": trainNo,
        "from_station_no": fromStationNo,
        "to_station_no": toStationNo,
        "seat_types": seatTypes,
        "train_date": trainDate
    }
    seatPrice = bot.getJson(api.QUERY_TICKET_PRICE, params=params)

    # 若返回数据错误，则5秒后重新调用
    if seatPrice["code"] != 200:
        print("数据返回错误，将于5秒后重新发起,错误原因：",seatPrice["msg"])
        time.sleep(5)
        return getSeatPrice(trainNo, fromStationNo, toStationNo, seatTypes, trainDate)
    seatPriceJson = seatPrice["data"]
    return util.dealSeatType(seatPriceJson,seatTypes)

# 确认车次订单
def submitTrainOrder(buyTrainInfo,trainFromStation,trainToStation):
    data = {
        "secretStr": buyTrainInfo["secretStr"],
        "train_date": buyTrainInfo["trainDate"],
        "back_train_date": "2025-02-05",
        "tour_flag": "dc",
        "purpose_codes": "ADULT",
        "query_from_station_name": trainFromStation,
        "query_to_station_name": trainToStation,
        "bed_level_info": "",
        "seat_discount_info": "",
        "undefined": ""
    }
    bot.postJson(api.SUBMIT_TICKET, data=data)


# 获取token与formJSon后续据此发送请求
def initDc():
    global globalRepeatSubmitToken
    global ticketInfoForPassengerForm
    # 首先获取token，后续需根据此token发送请求
    initDcResp = bot.post(api.INIT_DC, data={"_json_att": ""})

    # 提取globalRepeatSubmitToken和ticketInfoForPassengerForm
    globalRepeatSubmitToken = re.search(r"var globalRepeatSubmitToken = '(\w+)';", initDcResp.text)
    ticketInfoForPassengerForm = re.search(r'var ticketInfoForPassengerForm=(\{.*?\});', initDcResp.text, re.DOTALL)
    if not globalRepeatSubmitToken or not ticketInfoForPassengerForm:
        if not isLogin():
            print("登录失效，请重新登录")
            login()
            print("请稍等，将在4秒后重新获取乘车人信息")
            time.sleep(4)
            return getUserInfo()
        else:
            raise Error.ExitError("未知错误,globalRepeatSubmitToken与ticketInfoForPassengerForm获取不到，且已登录")
    else:
        globalRepeatSubmitToken = globalRepeatSubmitToken.group(1)
        ticketInfoForPassengerForm = json.loads(ticketInfoForPassengerForm.group(1).replace("'",'"'))

# 获取乘车人信息
def getUserInfo() ->list:
    # 获取乘车人信息
    data = {
        "_json_att": "",
        "REPEAT_SUBMIT_TOKEN": globalRepeatSubmitToken
    }
    userInfo = bot.postJson(api.GET_PASSENGER,data=data)["data"]
    if not userInfo["data"]["isExist"]:
        if isLogin():
            print(userInfo["data"]["exMsg"])
            time.sleep(random.randint(3,6))
            return getUserInfo()
        else:
            print("登录失效，请重新登录")
            login()
            return getUserInfo()

    num = 1
    usersInfo = userInfo["data"]["normal_passengers"]
    for user in usersInfo:
        user["no"] = num
        num += 1
    tb = pt.PrettyTable()
    tb.field_names = ['序号', '姓名', '电话', '证件号码']
    for user in usersInfo:
        tb.add_row(
            [user["no"], user["passenger_name"], user["mobile_no"] or "--", user["passenger_id_no"] or "--"]
        )
    print(tb)

    return usersInfo

# 选择席位
def getSeatInfo(trainInfo,userInfo):
    result = {}
    for index in range(0,len(userInfo)):
        user = userInfo[index]
        userInputSeat = util.userInput("请为" + user["passenger_name"] + '（' + user['passenger_id_no'] + '）' + "选择座位席别（如：商务座/特等座、二等座。若要选择商务座请输入“商务座/特等座”）", str)
        seatInfo = getSeatPrice(trainInfo["trainNo"], trainInfo["fromStationCode"], trainInfo["toStationCode"],
                            trainInfo["seatType"], trainInfo["trainDate"])
        for seatItem in seatInfo:
            if seatItem:
                if (seatItem["seatName"] == userInputSeat):
                    result[user["passenger_uuid"]] = seatItem

        if (len(result.keys()) != index+1):
            tb = pt.PrettyTable()
            tb.field_names = ["坐席名称","价格"]
            print("未找到坐席类型：",userInputSeat,"，下方是该列车的所有坐席，请根据下方坐席类别输入")
            print(seatInfo)
            for seatItem in seatInfo:
                if seatItem and seatItem["seatName"] != "未更新":
                    tb.add_row([seatItem["seatName"], seatItem["price"]])
            print(tb)
            return getSeatInfo(trainInfo,userInfo)
    return result

# 提交表单，返回第一个乘车人的seatType
def submitForm(buyUserInfos:list,buySeatInfos:dict):
    print("-> 1.正在提交表单")
    global globalRepeatSubmitToken
    data = {
        "cancel_flag": 2,
        "bed_level_order_num": "000000000000000000000000000000",
        "passengerTicketStr": "",
        "oldPassengerStr": "",
        "tour_flag": "dc",
        "whatsSelect": "1",
        "sessionId":"",
        "sig":"",
        "scene": "nc_login",
        "_json_att":"",
        "REPEAT_SUBMIT_TOKEN": globalRepeatSubmitToken
    }

    # 拼凑data的passengerTicketStr和oldPassengerStr字段
    # passengerTicketStr格式：seatType,0,ticket_type_codes,passenger_name,passenger_id_type_code,passenger_id_no,mobile_no,N,allEncStr
    # oldPassengerStr格式：passenger_name,passenger_id_type_code,passenger_id_no,ticket_type_codes
    # ticket_type_codes：代表成人票，学生票，儿童票等
    for buyUserInfo in buyUserInfos:
        passenger_uuid = buyUserInfo["passenger_uuid"]
        seatType = buySeatInfos[passenger_uuid]["seatType"]
        # 统一设为成人票
        ticket_type_codes = "1"
        # 拼凑passengerTicketStr字符串
        data["passengerTicketStr"] += seatType+",0,"+ticket_type_codes+","+buyUserInfo["passenger_name"]+","+buyUserInfo["passenger_id_type_code"]+","+buyUserInfo["passenger_id_no"]+","+buyUserInfo["mobile_no"]+",N,"+buyUserInfo["allEncStr"]+"_"
        # 拼凑oldPassengerStr字符串
        data["oldPassengerStr"] += buyUserInfo["passenger_name"]+","+buyUserInfo["passenger_id_type_code"]+","+buyUserInfo["passenger_id_no"]+","+ticket_type_codes+"_"
    data["passengerTicketStr"] = data["passengerTicketStr"][:-1]

    submitFormJson = bot.postJson(api.CHECK_USER_INFO, data=data)["data"]

    if not submitFormJson["status"]:
        raise Error.ExitError(submitFormJson["messages"])
    if submitFormJson["status"] and not submitFormJson["data"]["submitStatus"]:
        raise Error.ExitError(submitFormJson["data"]["errMsg"])

    return data
# 获取余票
def getQueueCount(seatType):
    print("-> 2.正在获取余票")
    data = {
        "train_date": "",
        "train_no": "",
        "stationTrainCode": "",
        "seatType": seatType,
        "fromStationTelecode": "",
        "toStationTelecode": "",
        "leftTicket": "",
        "purpose_codes": "",
        "train_location": "",
        "_json_att": "",
        "REPEAT_SUBMIT_TOKEN": globalRepeatSubmitToken
    }
    orderRequestDTO = ticketInfoForPassengerForm["orderRequestDTO"]

    dtObject = datetime.datetime.fromtimestamp(orderRequestDTO["train_date"]["time"] / 1000)
    data["train_date"] = dtObject.strftime("%a %b %d %Y %H:%M:%S GMT+0800 (伊尔库茨克标准时间)")
    data["train_no"] = orderRequestDTO["train_no"]
    data["stationTrainCode"] = orderRequestDTO["station_train_code"]
    data["fromStationTelecode"] = orderRequestDTO["from_station_telecode"]
    data["toStationTelecode"] = orderRequestDTO["to_station_telecode"]
    data["leftTicket"] = ticketInfoForPassengerForm["queryLeftTicketRequestDTO"]["ypInfoDetail"]
    data["purpose_codes"] = ticketInfoForPassengerForm["queryLeftTicketRequestDTO"]["purpose_codes"]
    data["train_location"] = ticketInfoForPassengerForm["train_location"]

    queueCount = bot.postJson(api.GET_QUEUE_COUNT, data=data)["data"]
    print("当前剩余票数：",queueCount["data"]["ticket"]," 排队人数：",queueCount["data"]["count"])

# 下单，单程票
def confimSingleTick(subitFormData):
    print("-> 3.正在提交购买队列")
    data = {
        "passengerTicketStr":subitFormData["passengerTicketStr"],
        "oldPassengerStr":subitFormData["oldPassengerStr"],
        "purpose_codes":ticketInfoForPassengerForm["queryLeftTicketRequestDTO"]["purpose_codes"],
        "key_check_isChange":ticketInfoForPassengerForm["key_check_isChange"],
        "leftTicketStr":ticketInfoForPassengerForm["queryLeftTicketRequestDTO"]["ypInfoDetail"],
        "train_location":ticketInfoForPassengerForm["train_location"],
        "choose_seats":"", # 选座，目前随机座位
        "seatDetailType":"000",
        "is_jy":"N",
        "is_cj":"N",
        "encryptedData":"",
        "whatsSelect":"1",
        "roomType":"00",
        "dwAll":"N",
        "_json_att":"",
        "REPEAT_SUBMIT_TOKEN":globalRepeatSubmitToken
    }

    confirmSingleForQueue = bot.postJson(api.CONFIM_SINGLE_TICKET,data=data)["data"]
    if confirmSingleForQueue["data"]["submitStatus"]:
        print("进入购买队列成功!")
    else:
        raise Error.ExitError(confirmSingleForQueue["data"]["errMsg"])

# 轮询，查询状态
def queryOrder():
    print("-> 4.正在查询订单状态")
    while True:
        a = {
            "dispTime":100,
            "nextRequestTime":2
        }
        params = {
            "random":int(time.time()*1000),
            "tourFlag":"dc",
            "_json_att":"",
            "REPEAT_SUBMIT_TOKEN":globalRepeatSubmitToken
        }
        orderStatus = bot.getJson(api.QUERY_ORDER_WAIT_TIME,params=params)["data"]
        if not orderStatus["data"]["queryOrderWaitTimeStatus"]:
            raise Error.ExitError("查询错误，未知错误")
        else:
            waitTime = orderStatus["data"]["waitTime"]
            if waitTime != -100:
                a["dispTime"] = waitTime
                d = int(waitTime / 1.5)
                d = 60 if d > 60 else d
                b = waitTime - d
                a["nextRequestTime"] = 1 if b <= 0 else b

                # 此时已获取结果
                if a["dispTime"] <= 0:
                    if not orderStatus["data"]["orderId"]:
                        print(orderStatus["data"]["msg"])
                        break
                    else:
                        print("购票成功！")
                        break

            time.sleep(a["nextRequestTime"])




if __name__ == '__main__':
    # 初始化init
    config = Config.Config()
    if config.debug:
        logger = Logger.Logger(Logger.DEBUG)
    else:
        logger = Logger.Logger(Logger.INFO)

    bot = Bot.Bot(logger)
    util = Util.Util()
    api = Api.Api()

    # 12306全局token
    globalRepeatSubmitToken = ""
    ticketInfoForPassengerForm = {}

    # 登录
    login()

    # 获取并打印车次信息
    trainDate = util.userInput("请输入要买票的车次日期，格式：2024-01-20",str)
    trainFromStation = util.userInput("请输入始发地",str)
    trainToStation = util.userInput("请输入目的地",str)
    trainsInfo = getTrainInfo(trainDate , util.getCityCode(trainFromStation) ,util.getCityCode(trainToStation))

    # 选择要买票的车次
    buyTrainInfo = {}
    trainNo = util.userInput("请输入要买票的车次序号", int)
    for trainInfo in trainsInfo:
        if trainInfo["no"] == trainNo:
            buyTrainInfo = trainInfo
    if buyTrainInfo == {}:
        raise Error.ExitError("未找到车次序号；"+str(trainNo))

    # 提交车次订单
    submitTrainOrder(buyTrainInfo,trainFromStation,trainToStation)

    # 获取init界面
    initDc()

    # 获取并打印人员信息
    usersInfo = getUserInfo()

    # 选择乘车人
    buyUserInfos = []
    userChooseNos = util.userInput("请选择乘车人的序号，用空格分割多个乘车人（如：1 2 3）", str).split(" ")
    for userChooseNo in userChooseNos:
        if userChooseNo:
            try:
                userChooseNo = int(userChooseNo)
                if (userChooseNo <= 0 or userChooseNo > len(usersInfo)):
                    raise Error.InputError("请按照提示输入")
            except ValueError:
                raise Error.InputError("请按照提示输入")
            for userInfo in usersInfo:
                if userChooseNo == userInfo["no"]:
                    buyUserInfos.append(userInfo)


    # 选择席位
    buySeatInfos = getSeatInfo(buyTrainInfo,buyUserInfos)

    print("--------开始买票--------")
    # 提交表单，获取data，后续需要据此发送请求
    subitFormData = submitForm(buyUserInfos,buySeatInfos)

    # 获取余票，需要第一个乘车人的seatType
    getQueueCount(subitFormData["passengerTicketStr"].split(",")[0])

    # 下单，进入队列
    confimSingleTick(subitFormData)

    # 轮询，查看状态
    queryOrder()