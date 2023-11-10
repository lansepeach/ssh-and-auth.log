import re
import glob
from collections import defaultdict
from datetime import datetime

# 用于匹配SSH登录成功和失败的正则表达式模式
success_pattern = r"(\w{3}\s+\d{1,2} \d{2}:\d{2}:\d{2}) .+ Accepted publickey for (.+) from (.+) port (\d+)"
failure_pattern = r"(\w{3}\s+\d{1,2} \d{2}:\d{2}:\d{2}) .+ Failed password for (.+) from (.+) port (\d+)"

# 用于存储登录统计信息的字典
login_stats = defaultdict(lambda: {"success": 0, "failure": 0, "login_history": []})

# 读取SSH登录日志文件
log_file_paths = sorted(glob.glob("/var/log/auth.log*"), reverse=True)  # 获取所有的日志文件，并按照文件名降序排序

# 添加感叹号以表示登录失败
EXCLAMATION_MARK = "❗"

for log_file_path in log_file_paths:
    try:
        with open(log_file_path, "r", encoding='utf-8', errors='ignore') as auth_log:
            for line in auth_log:
                if "sshd" in line:
                    # 尝试匹配成功和失败的登录记录
                    success_match = re.search(success_pattern, line)
                    failure_match = re.search(failure_pattern, line)

                    if success_match:
                        username = success_match.group(2)
                        source_ip = success_match.group(3)
                        port = success_match.group(4)
                        login_time = datetime.strptime(success_match.group(1), "%b %d %H:%M:%S")
                        login_stats[username]["success"] += 1
                        login_stats[username]["login_history"].append((source_ip, port, "成功", login_time))
                    elif failure_match:
                        username = failure_match.group(2)
                        source_ip = failure_match.group(3)
                        port = failure_match.group(4)
                        login_time = datetime.strptime(failure_match.group(1), "%b %d %H:%M:%S")
                        login_stats[username]["failure"] += 1
                        login_stats[username]["login_history"].append((source_ip, port, f"{EXCLAMATION_MARK}失败", login_time))
    except FileNotFoundError:
        print(f"日志文件 {log_file_path} 未找到。请检查文件路径是否正确。")
        continue  # 如果文件不存在，继续处理下一个文件
    except PermissionError:
        print(f"权限错误。无法读取日志文件 {log_file_path}。请以具有读取日志文件权限的用户运行此脚本。")
        continue  # 如果无法读取文件，继续处理下一个文件

# 打印登录统计信息
for username, stats in login_stats.items():
    total_success = stats["success"]
    total_failures = stats["failure"]
    login_history = sorted(stats["login_history"], key=lambda x: x[3], reverse=True)[:10]  # 获取最近的10个登录历史记录

    print(f"用户: {username}")
    print(f"成功登录次数: {total_success}")
    print(f"失败登录次数: {total_failures}")
    
    if login_history:
        print("登录历史 (最近10个):")
        for ip, port, result, time in login_history:
            print(f"  IP地址: {ip}, 端口: {port}, 结果: {result}, 时间: {time.strftime('%m-%d %H:%M:%S')}")
            
    print()

# 询问用户是否导出全部的登录历史记录
export_choice = input("是否导出全部的登录历史记录到log.txt文件中？(y/n): ")
if export_choice.lower() == 'y':
    with open('log.txt', 'w') as f:
        for username, stats in login_stats.items():
            f.write(f"用户: {username}\n")
            f.write(f"成功登录次数: {stats['success']}\n")
            f.write(f"失败登录次数: {stats['failure']}\n")
            if stats['login_history']:
                f.write("全部登录历史:\n")
                for ip, port, result, time in sorted(stats['login_history'], key=lambda x: x[3]):
                    f.write(f"  IP地址: {ip}, 端口: {port}, 结果: {result}, 时间: {time.strftime('%m-%d %H:%M:%S')}\n")
            f.write("\n")
