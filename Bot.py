import requests
import Logger
from requests import Response
from requests import JSONDecodeError
import Error

class Bot:
    def __init__(self,logger:Logger):
        self.baseReq = requests
        self.req = self.baseReq.session()
        self.logger = logger

        # 配置基本请求头
        baseHeader = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.47"
        }
        self.req.headers["User-Agent"] = baseHeader["User-Agent"]

    def getJson(self,url:str,
            params=None)->dict:
        try:
            resp = self.req.get(url=url,params=params)
            logMsg = f"请求地址：{resp.url}, 返回数据：{resp.text}"
            self.logger.debug(logMsg)
            if resp.status_code != 200:
                result = {
                    "code": 500,
                    "data": None,
                    "msg": "请求错误，错误码："+str(resp.status_code)
                }
                return result
            json = resp.json()
            result = {
                "code":200,
                "data":json,
                "msg":"正常返回"
            }
            return result
        except JSONDecodeError:
            result = {
                "code": 400,
                "data": None,
                "msg": "无法解析成Json格式,原数据：\n"+resp.text
            }
            return result

    def postJson(self,url:str,
            data=None)->dict:
        try:
            resp = self.req.post(url=url,data=data)
            logMsg = f"请求地址：{resp.url}, 返回数据：{resp.text}"
            self.logger.debug(logMsg)
            if resp.status_code != 200:
                result = {
                    "code": 500,
                    "data": None,
                    "msg": "请求错误，错误码：" + str(resp.status_code)
                }
                return result
            json = resp.json()

            if "status" in json:
                if not json["status"]:
                    raise Error.ExitError(json["messages"])
            result = {
                "code": 200,
                "data": json,
                "msg": "正常返回"
            }
            return result
        except JSONDecodeError:
            result = {
                "code": 400,
                "data": None,
                "msg": "无法解析成Json格式,原数据：\n" + resp.text
            }
        return result

    def post(self,url:str,
            data=None)->Response:
        resp = self.req.post(url=url, data=data)
        logMsg = f"请求地址：{resp.url}, 返回数据：{resp.text}"
        self.logger.debug(logMsg)

        return resp
