# ssh-and-auth.log
关于ssh的登录日志方便国人查看分析的脚本，可以显示出最近的10条每个用户的登录日志和导出全部的日志(这是使用chatgpt4生成的)



该脚本可以读取所有的轮转日志文件，比如auth.log.1, auth.log.2等，
## 使用方法


下载sshlog.py文件

wget https://raw.githubusercontent.com/lansepeach/ssh-and-auth.log/main/sshlog.py

需要在ubuntu下安装python

运行脚本
sudo python3 sshlog.py  
