# 一、项目说明：
本项目用于自动购买122306车票

# 二、目录概要：
### 文件夹
`cityCode文件夹`：用于存放12306城市和城市代码的json数据<br>
`config文件夹`:用于存放配置文件，内有每个配置的详细说明<br>
`cookie文件夹`:存放cookie信息<br>
`js文件夹`:存放12306前端js代码<br>

### 文件
`12306QrCode.jpg`:当使用扫码登录时，显示在本地的jpg文件<br>
`Api.py`:12306的Api<br>
`Bot.py`:封装requests库，自定义请求<br>
`Config.py`:用于读取配置文件<br>
`Error.py`:自定义Error<br>
`Logger.py`:日志对象，封装logging<br>
`Util.py`:工具<br>
`main.py`:程序入口<br>

# 三、如何使用：
1. 安装依赖
````
pip install -r requirements.txt
````

2.运行`main.py`文件

# 四、报错及处理：
若报错
````
filenotfounderror: could not find module ‘libiconv.dll‘
````
libiconv.dll需要安装动态连接库，[点此下载](https://download.microsoft.com/download/F/3/5/F3500770-8A08-488E-94B6-17A1E1DD526F/vcredist_x64.exe)，下载完以后双击安装，安装好即可