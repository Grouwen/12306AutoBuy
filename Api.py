class Api():
    BASE_URL = "https://kyfw.12306.cn"

    # 登录相关API
    LOGIN_BY_QR_CODE = BASE_URL + "/passport/web/create-qr64"
    LOGIN_BY_QR_CODE_CHECK = BASE_URL + "/passport/web/checkqr"
    LOGIN_URL = BASE_URL + "/passport/web/login"
    LOGIN_CHECK_VERIFY = BASE_URL + "/passport/web/checkLoginVerify"
    LOGIN_BY_MESSAGECODE = BASE_URL + "/passport/web/getMessageCode"
    LOGIN_CONFIM = BASE_URL + "/otn/login/conf"

    # 初始化12306相关API
    INIT_12306 = BASE_URL + "/otn/index/initMy12306Api"
    INIT_UAMTK = BASE_URL + "/passport/web/auth/uamtk"
    INIT_UAMTK_CLIENT = BASE_URL + "/otn/uamauthclient"

    # 查询车票等信息的相关API
    QUERY_LEFT_TICKET = BASE_URL + "/otn/leftTicket/query"
    QUERY_TICKET_PRICE = BASE_URL + "/otn/leftTicket/queryTicketPrice"
    SUBMIT_TICKET = BASE_URL + "/otn/leftTicket/submitOrderRequest"

    # 初始化initDC页面
    INIT_DC = BASE_URL + "/otn/confirmPassenger/initDc"

    # 获取人员信息
    GET_PASSENGER = BASE_URL + "/otn/confirmPassenger/getPassengerDTOs"

    # 检查用户信息
    CHECK_USER_INFO = BASE_URL + "/otn/confirmPassenger/checkOrderInfo"

    # 获取余票信息
    GET_QUEUE_COUNT = BASE_URL + "/otn/confirmPassenger/getQueueCount"

    # 进入购买队列，单程票
    CONFIM_SINGLE_TICKET = BASE_URL + "/otn/confirmPassenger/confirmSingleForQueue"

    # 查询购买状态
    QUERY_ORDER_WAIT_TIME = BASE_URL + "/otn/confirmPassenger/queryOrderWaitTime"
