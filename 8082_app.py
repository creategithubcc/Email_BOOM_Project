# -*- coding: utf-8 -*-
import json
from flask import Flask, render_template, request
import imaplib
import email
import sys
from email.header import decode_header
import os
import re
import threading
import time

app = Flask(__name__)

lock = threading.Lock()

#定义什么时候比赛
day01='04'
day02='05'
day03='06'
day04='07'
day05='08'

dmarc_list = []
DMARK_LIST = {}#DMARC_TOP_10000_Output.txt
with open('DMARC_TOP_10000_Output.txt', 'r') as file:
    for line in file:
        try:
            DMARK_LIST = json.loads(line)
            domain = list(DMARK_LIST.keys())[0]  # 提取第一个键，即域名
            dmarc_list.append(domain)
        except ValueError:
            continue

top_domains_file = "Tranco-top-10000-domains.txt"
#top_domains_file = "Secrank.txt"
mail_select= ["Inbox"]
Team = {
            "test@mail10.nospoofing.cn": "测试战队",
        }

COLORS = {
    'red': '\033[91m',
    'green': '\033[92m',
    'yellow': '\033[93m',
    'blue': '\033[94m',
    'magenta': '\033[95m',
    'cyan': '\033[96m',
    'white': '\033[97m',
    'bold': '\033[1m',
    'italic': '\033[3m',
    'underline': '\033[4m',
    'inverse': '\033[7m',
    'hidden': '\033[8m',
    'reset': '\033[0m',
}

DMARK_LIST = {}#DMARC_TOP_10000_Output.txt

def colored_print(color, text):
    sys.stdout.write(COLORS[color] + text + COLORS['reset'] + '\n')
    sys.stdout.flush()

def get_top_domains(filename): #获取Tranco-top-10000-domains.txt域名
    with open(filename, "r") as file:
        return [line.strip() for line in file]

def extract_domain(email_address): #提取邮件账号@后面的域名
    match = re.search(r"@([\w.-]+)", email_address)
    if match:
        return match.group(1)
    return None

def is_subdomain(subdomain, domain): #判断是否是子域名
    return subdomain.endswith("." + domain) or subdomain == domain

def calculate_score(domain, top_domains): #计算分数
    if domain in top_domains[:100]:
        return 5
    elif domain in top_domains[101:1000]:
        return 3
    elif domain in top_domains[1001:10000]:
        return 1
    return 0

def process_emails_single_email(domain, top_domains_file, domain_scores, answer_scores, pass_score,day_result): #处理单个邮件，的给分情况
    top_domains = get_top_domains(top_domains_file)

    if domain:
        for top_domain in top_domains:
            if is_subdomain(domain, top_domain):
                if top_domain not in domain_scores:
                    domain_scores[top_domain] = {f"{day01}_score": 0, f"{day01}_count": 0,f"{day02}_score": 0, f"{day02}_count": 0,f"{day03}_score": 0, f"{day03}_count": 0,f"{day04}_score": 0, f"{day04}_count": 0,f"{day05}_score": 0, f"{day05}_count": 0}

                if domain_scores[top_domain][f"{day_result}_count"] < 10:#每个域名最多计算10次
                    domain_scores[top_domain][f"{day_result}_score"] += calculate_score(top_domain, top_domains) * pass_score
                    answer_scores[f"{day_result}_Score"] += calculate_score(top_domain, top_domains) * pass_score
                    if pass_score != 0:
                        domain_scores[top_domain][f"{day_result}_count"] += 1  # 计算次数加1
                        answer_scores[f"{day_result}_Email_Nums"] += 1  # 邮件数量加1
                break
        answer_scores["max_Score"] = max(answer_scores[f"{day01}_Score"],answer_scores[f"{day02}_Score"],answer_scores[f"{day03}_Score"],answer_scores[f"{day04}_Score"],answer_scores[f"{day05}_Score"]) #最高分

def fetch_and_save_emails(email_address, password, domain_scores, answer_scores,b,start_email_id,end_email_id): #获取邮件并保存
    try:
        #start_login_time = time.time()

        mail = imaplib.IMAP4_SSL("120.24.255.190", 993)
        mail.login(email_address, password)

        #end_login_time = time.time() - start_login_time
        #colored_print(b,f"{email_address} login time: {end_login_time:.2f}s")

        folder_name = email_address.replace("@", "_").replace(".", "_") #将邮箱地址中的@和.替换成_

        #folder_name = folder_name + "_" + b #加上b标识，区分不同的邮箱

        os.makedirs(folder_name, exist_ok=True) #创建文件夹

        file_path = f"{folder_name}/{email_address}_email_ids.txt" #存储邮件id的文件

        for i in mail_select:
            mail.select(i)
            status, messages = mail.search(None, "ALL")
            email_ids = messages[0].split()  # 邮件id

            if end_email_id > len(email_ids):
                print(f"邮箱{email_address}邮件总数{len(email_ids)}，你输入的结束邮件 {end_email_id} 大于邮件总数，将自动设置为{len(email_ids)}")
                end_email_id = len(email_ids)

            latest_email_ids = []
            if start_email_id < end_email_id:
                #colored_print(b, f"开始拉区间{start_email_id}到{end_email_id}的邮件")
                latest_email_ids = email_ids[start_email_id:end_email_id]  # 先获取最新的10封邮件
            else:
                print(f"邮箱{email_address}开始邮件id {start_email_id} >= 结束邮件id {end_email_id}，将等待10s后自动跳过该回合！")
                time.sleep(10)

            with lock: #加锁是为了防止多线程的情况下数据乱了，毕竟用的变量是一样的
                dmarc_flag = False
                with open(file_path, "a") as file:
                    for email_id_bytes in latest_email_ids:#想要所有的话就换成email_ids
                        email_id_str = email_id_bytes.decode("utf-8")

                        status, msg_data = mail.fetch(email_id_str, "(RFC822)")
                        raw_email = msg_data[0][1]
                        file.write(email_id_str + "\n")

                        with open(f"{folder_name}/{email_id_str}.txt", "w") as email_file:  # 将邮件内容写入文件
                            msg = email.message_from_bytes(raw_email)

                            try:
                                for header in ["From", "Subject", "Date"]:
                                    value, charset = decode_header(msg[header])[0]
                                    if isinstance(value, bytes):
                                        value = value.decode(charset if charset else "utf-8")
                                    email_file.write(f"{header}: {value}\n")

                                authentication_results = msg.get("Authentication-Results", "")
                                email_file.write(f"Authentication-Results: {authentication_results}\n")

                                time_results = msg.get("Received", "")
                                email_file.write(f"Received: {time_results}\n")

                            except Exception as e:
                                colored_print(b, f"{email_address}: 再读取信头: {email_id_str} 的时候发现没有关键字段: {str(e)}")

                            domain = extract_domain(msg["From"])
                            pass_score = 0
                            authentication_results = msg.get("Authentication-Results", "")
                            authentication_results = re.sub(r'\s+[\t\n]', '', authentication_results).strip()

                            time_results = msg.get("Received", "")
                            time_results = re.sub(r'\s+[\t\n]', '', time_results).strip()
                            cur_time = re.search(r'(\d{2}:\d{2}:\d{2})', time_results)

                            try:
                                day_result = re.search(r'(\d{2}\s)', time_results)
                                day_result = day_result.group(0).strip()
                            except Exception as e:
                                day_result = "00"
                                #print("day_result:", day_result)
                            #print("day_result:", day_result)

                            time_stamp = 0
                            if cur_time:
                                time_stamp = cur_time.group(1)  # 获取匹配的时间戳字符串
                                time_stamp = time_stamp.replace(':', '')  # 去除冒号

                                if time_stamp:
                                    time_stamp = int(time_stamp)  # 将时间戳字符串转换为整数
                                    #print("转换后的整数时间戳:", time_stamp)
                            #     else:
                            #         print("时间戳字符串为空")
                            # else:
                            #     print("未找到匹配的时间戳")

                            if 0 <= time_stamp <= 200000 and (day_result == day01 or day_result == day02 or day_result == day03 or day_result == day04 or day_result == day05):#时间戳在允许范围内
                                #colored_print(b, f"时间戳在允许范围内: {time_stamp},且日期为{day_result}号")
                                if "spf=pass" in authentication_results:
                                    pass_score += 1
                                    #print("spf=pass +1分")
                                    for i in dmarc_list:#通过初始的dmarc验证
                                        if domain.endswith("." + i) or domain.find("." + i + ".") != -1:
                                            matches2 = re.findall(r'smtp\.mail=[^\s@]+@([^\s>;]+)(?<!;)', authentication_results)#查看spf里的mail from域名和dmarc是否一样
                                            for match in matches2:
                                                if match.endswith("." + i) or match.find("." + i + ".") != -1 or domain.endswith("." + match) or domain.find("." + match + ".") != -1:
                                                    pass_score += 1  # 通过spf下的dmarc验证+1分
                                                    #print("通过spf下的dmarc验证+1分")
                                                    dmarc_flag = True
                                                    break  # 跳出当前的内层循环
                                        else:
                                            continue
                                        break

                                if "dkim=pass" in authentication_results:
                                    pass_score += 1
                                    #print("dkim=pass +1分")
                                    if not dmarc_flag:
                                        for i in dmarc_list:
                                            if domain.endswith("." + i) or domain.find("." + i + ".") != -1:
                                                matches = re.findall(r'header\.i=@([^\s;]+)', authentication_results)
                                                if matches:
                                                    for match in matches:
                                                        if match.endswith("." + i) or match.find("." + i + ".") != -1 or domain.endswith("." + match) or domain.find("." + match + ".") != -1:
                                                            pass_score += 1  # 通过dkim下的dmarc验证+1分
                                                            #print("通过dkim下的dmarc验证+1分")
                                                            break  # 跳出当前的内层循环
                                            else:
                                                continue
                                            break
                                dmarc_flag = False

                                #colored_print(b, f"pass_score: {pass_score}")

                                if domain:
                                    process_emails_single_email(domain, top_domains_file, domain_scores, answer_scores,
                                                                pass_score,day_result)
                            # else:
                            #     print("当前邮件的接收时间不在范围，不进行统计！")

                    if start_email_id < end_email_id:
                        #colored_print(b,f"{start_email_id}到{end_email_id}的邮件拉取完毕")
                        start_email_id = end_email_id
                        end_email_id = start_email_id + 10
                        #colored_print(b,f"下一次拉区间{start_email_id}到{end_email_id}的邮件")
                    else:
                        start_email_id = end_email_id
                        end_email_id = start_email_id + 10

    except Exception as e:
        colored_print(b,f"Error occurred while processing {email_address}: {str(e)}")

    return domain_scores, answer_scores, start_email_id, end_email_id,folder_name

def fetch_emails_periodically(email_address, password, all_teams_scores,b,start_email_id,end_email_id): #定时获取邮件
    # run_time = time.time()

    new_domain_scores = {}
    new_answer_scores = {"Rank": 1, "Team": Team[email_address], f'{day01}_Email_Nums': 0, f'{day01}_Score': 0, f'{day02}_Email_Nums': 0, f'{day02}_Score': 0, f'{day03}_Email_Nums': 0, f'{day03}_Score': 0, f'{day04}_Email_Nums': 0, f'{day04}_Score': 0, f'{day05}_Email_Nums': 0, f'{day05}_Score': 0,'max_Score': 0}
    #new_answer_scores = {"Rank": 1, "Team": Team[email_address], "Email_Nums": 0, "Score": 0}
    #new_answer_scores = {"Rank": 1, "Team": Team[email_address]+'_'+b, "Email_Nums": 0, "Score": 0}
    #new_answer_scores = {"Rank": 1, "Team": Team[email_address], "Email_Nums": random.randint(0, 10), "Score": random.randint(0, 100)}#假设排名成绩

    while True:
        #operation_time = time.time()
        domain_scores, answer_scores,start_email_id,end_email_id,folder_name = fetch_and_save_emails(email_address, password, new_domain_scores, new_answer_scores,b,start_email_id,end_email_id) #获取邮件并保存
        #end_operation_time = time.time() - operation_time
        #colored_print(b,f"{email_address} operation time: {end_operation_time:.2f}s")

        with lock:
            # colored_print(b,"############## Domain Scores ##############")
            # for domain, score_info in domain_scores.items():
                # colored_print(b,f"{domain}:\n\t\t{day01}_Score = {score_info[f'{day01}_score']}, {day01}_Count = {score_info[f'{day01}_count']},"
                #                 f"\n\t\t{day02}_Score = {score_info[f'{day02}_score']}, {day02}_Count = {score_info[f'{day02}_count']},"
                #                 f"\n\t\t{day03}_Score = {score_info[f'{day03}_score']}, {day03}_Count = {score_info[f'{day03}_count']},"
                #                 f"\n\t\t{day04}_Score = {score_info[f'{day04}_score']}, {day04}_Count = {score_info[f'{day04}_count']},"
                #                 f"\n\t\t{day05}_Score = {score_info[f'{day05}_score']}, {day05}_Count = {score_info[f'{day05}_count']}\n")

            # colored_print(b,"############## Answer Scores ##############")
            # colored_print(b,f"{answer_scores}")

            with open(f"{folder_name}/debug_msg.txt", "w") as email_file:#w是覆盖写入，a是追加写入
                email_file.write(f"############## Domain Scores ##############\n")
                for domain, score_info in domain_scores.items():
                    email_file.write(f"{domain}:\n\t\t{day01}_Score = {score_info[f'{day01}_score']}, {day01}_Count = {score_info[f'{day01}_count']},"
                                f"\n\t\t{day02}_Score = {score_info[f'{day02}_score']}, {day02}_Count = {score_info[f'{day02}_count']},"
                                f"\n\t\t{day03}_Score = {score_info[f'{day03}_score']}, {day03}_Count = {score_info[f'{day03}_count']},"
                                f"\n\t\t{day04}_Score = {score_info[f'{day04}_score']}, {day04}_Count = {score_info[f'{day04}_count']},"
                                f"\n\t\t{day05}_Score = {score_info[f'{day05}_score']}, {day05}_Count = {score_info[f'{day05}_count']}\n")
                email_file.write(f"############## Answer Scores ##############\n\n\n")
                email_file.write(f"{answer_scores}")


            found_existing_team = False #是否找到已经存在的队伍，这是对每次循环的战队分数排名时用的
            for i, team_data in enumerate(all_teams_scores): #如果已经存在就更新分数
                if team_data["Team"] == answer_scores["Team"]:
                    all_teams_scores[i] = answer_scores
                    found_existing_team = True #找到了已经存在的队伍
                    break

            if not found_existing_team: #如果没有找到已经存在的队伍就添加到all_teams_scores
                all_teams_scores.append(answer_scores)

def Show_Rank():
    global Final_Ranking_Aswer
    while True:
        print("先睡眠15s，等待所有线程都完成一轮")
        time.sleep(15)
        with lock:
            Final_Ranking_Aswer.clear()
            # print("清空Final_Ranking_Aswer")
            colored_print(b, "############## Teams Ranking ##############")
            all_teams_scores.sort(key=lambda x: x["max_Score"], reverse=True)
            current_rank = 1
            prev_score = all_teams_scores[0]["max_Score"]  # 第一名的分数
            for i, team_score in enumerate(all_teams_scores):  # enumerate()函数用于将一个可遍历的数据对象组合为一个索引序列，同时列出数据和数据下标
                if team_score["max_Score"] < prev_score:
                    current_rank = i + 1
                    prev_score = team_score["max_Score"]
                    all_teams_scores[i]['Rank'] = current_rank
                elif team_score["max_Score"] == prev_score:
                    all_teams_scores[i]['Rank'] = current_rank

                ranking_info = {
                    'Rank': current_rank,
                    'Team': team_score['Team'],
                    "day01": day01,
                    "day02": day02,
                    "day03": day03,
                    "day04": day04,
                    "day05": day05,
                    f'{day01}_Score': team_score[f'{day01}_Score'],
                    f'{day01}_Email_Nums': team_score[f'{day01}_Email_Nums'],
                    f'{day02}_Score': team_score[f'{day02}_Score'],
                    f'{day02}_Email_Nums': team_score[f'{day02}_Email_Nums'],
                    f'{day03}_Score': team_score[f'{day03}_Score'],
                    f'{day03}_Email_Nums': team_score[f'{day03}_Email_Nums'],
                    f'{day04}_Score': team_score[f'{day04}_Score'],
                    f'{day04}_Email_Nums': team_score[f'{day04}_Email_Nums'],
                    f'{day05}_Score': team_score[f'{day05}_Score'],
                    f'{day05}_Email_Nums': team_score[f'{day05}_Email_Nums'],
                    'max_Score': team_score['max_Score']
                }
                colored_print(b,f"'Rank': {current_rank}, 'Team': '{team_score['Team']}', "
                                f"'{day01}_Score': {team_score[f'{day01}_Score']}, '{day01}_Email_Nums': {team_score[f'{day01}_Email_Nums']}, "
                                f"'{day02}_Score': {team_score[f'{day02}_Score']}, '{day02}_Email_Nums': {team_score[f'{day02}_Email_Nums']}, "
                                f"'{day03}_Score': {team_score[f'{day03}_Score']}, '{day03}_Email_Nums': {team_score[f'{day03}_Email_Nums']}, "
                                f"'{day04}_Score': {team_score[f'{day04}_Score']}, '{day04}_Email_Nums': {team_score[f'{day04}_Email_Nums']}, "
                                f"'{day05}_Score': {team_score[f'{day05}_Score']}, '{day05}_Email_Nums': {team_score[f'{day05}_Email_Nums']}, "
                                f"max_Score: {team_score['max_Score']}")

                Final_Ranking_Aswer.append(ranking_info)

            #print(Final_Ranking_Aswer)
            #colored_print(b, f"{all_teams_scores}")  # 查看目前所有排名信息

@app.route('/')
def index():
    ans = Final_Ranking_Aswer
    #print(ans)
    return render_template('ScoreWebsite.html', res=ans)

@app.route('/debug_index')
def debug_index():
    return render_template('debug_index.html')

@app.route('/get_debug_msg', methods=['POST'])
def debug_msg():
    folder_name = request.form['folder_name']
    debug_msg_file_path = os.path.join(folder_name, 'debug_msg.txt')
    try:
        with open(debug_msg_file_path, 'r') as file:
            debug_msg_content = file.read()
        return render_template('get_debug_msg.html', debug_msg_content=debug_msg_content)
    except FileNotFoundError:
        return "File not found"

if __name__ == "__main__":
    accounts = [
        #("test@mail10.nospoofing.cn", "password"),
    ]

    threads = []
    all_teams_scores = []  # 存储所有队伍的得分信息
    Final_Ranking_Aswer = []  # 存储最终排名信息

    worker_id = 0
    a = list(COLORS.keys())

    accounts_num = len(accounts)

    for email_address, password in accounts:
        start_email_id = int(worker_id / accounts_num)
        end_email_id = start_email_id + 10

        worker_id += 1
        b = a[worker_id - 1]

        thread = threading.Thread(target=fetch_emails_periodically, args=(
        email_address, password, all_teams_scores, b, start_email_id,
        end_email_id))
        threads.append(thread)
        thread.start()

    Rank_thread = threading.Thread(target=Show_Rank)
    Rank_thread.start()

app.run(host='0.0.0.0', port=8082, debug=True)
