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
            "security@mail10.nospoofing.cn": "安全0战队",
            "security1@mail10.nospoofing.cn": "安全1战队",
            "security2@mail10.nospoofing.cn": "安全2战队",
            "security3@mail10.nospoofing.cn": "安全3战队",
            "security4@mail10.nospoofing.cn": "安全4战队",
            "security5@mail10.nospoofing.cn": "安全5战队",
            "security6@mail10.nospoofing.cn": "安全6战队",
            "security7@mail10.nospoofing.cn": "安全7战队",
            "security8@mail10.nospoofing.cn": "安全8战队",
            "security9@mail10.nospoofing.cn": "安全9战队",
            "security10@mail10.nospoofing.cn": "安全10战队",
            "security11@mail10.nospoofing.cn": "安全11战队",
            "security12@mail10.nospoofing.cn": "安全12战队",
            "security13@mail10.nospoofing.cn": "安全13战队",
            "security14@mail10.nospoofing.cn": "安全14战队",
            "security15@mail10.nospoofing.cn": "安全15战队",
            "security16@mail10.nospoofing.cn": "安全16战队",
            "security17@mail10.nospoofing.cn": "安全17战队",
            "security18@mail10.nospoofing.cn": "安全18战队",
            "security19@mail10.nospoofing.cn": "安全19战队",
            "security20@mail10.nospoofing.cn": "安全20战队",
            "security21@mail10.nospoofing.cn": "安全21战队",
            "security22@mail10.nospoofing.cn": "安全22战队",
            "security23@mail10.nospoofing.cn": "安全23战队",
            "security24@mail10.nospoofing.cn": "安全24战队",
            "security25@mail10.nospoofing.cn": "安全25战队",
            "security26@mail10.nospoofing.cn": "安全26战队",
            "security27@mail10.nospoofing.cn": "安全27战队",
            "security28@mail10.nospoofing.cn": "安全28战队",
            "security29@mail10.nospoofing.cn": "安全29战队",
            "security30@mail10.nospoofing.cn": "安全30战队",
            "security31@mail10.nospoofing.cn": "安全31战队",
            "security32@mail10.nospoofing.cn": "安全32战队",
            "security33@mail10.nospoofing.cn": "安全33战队",
            "security34@mail10.nospoofing.cn": "安全34战队",
            "security35@mail10.nospoofing.cn": "安全35战队",
            "security36@mail10.nospoofing.cn": "安全36战队",
            "security37@mail10.nospoofing.cn": "安全37战队",
            "security38@mail10.nospoofing.cn": "安全38战队",
            "security39@mail10.nospoofing.cn": "安全39战队",
            "security40@mail10.nospoofing.cn": "安全40战队",
            "security41@mail10.nospoofing.cn": "安全41战队",
            "security42@mail10.nospoofing.cn": "安全42战队",
            "security43@mail10.nospoofing.cn": "安全43战队",
            "security44@mail10.nospoofing.cn": "安全44战队",
            "security45@mail10.nospoofing.cn": "安全45战队",
            "security46@mail10.nospoofing.cn": "安全46战队",
            "security47@mail10.nospoofing.cn": "安全47战队",
            "security48@mail10.nospoofing.cn": "安全48战队",
            "security49@mail10.nospoofing.cn": "安全49战队",
            "security50@mail10.nospoofing.cn": "安全50战队",
            "security51@mail10.nospoofing.cn": "安全51战队",
            "security52@mail10.nospoofing.cn": "安全52战队",
            "security53@mail10.nospoofing.cn": "安全53战队",
            "security54@mail10.nospoofing.cn": "安全54战队",
            "security55@mail10.nospoofing.cn": "安全55战队",
            "security56@mail10.nospoofing.cn": "安全56战队",
            "security57@mail10.nospoofing.cn": "安全57战队",
            "security58@mail10.nospoofing.cn": "安全58战队",
            "security59@mail10.nospoofing.cn": "安全59战队",
            "security60@mail10.nospoofing.cn": "安全60战队",
            "security61@mail10.nospoofing.cn": "安全61战队",
            "security62@mail10.nospoofing.cn": "安全62战队",
            "security63@mail10.nospoofing.cn": "安全63战队",
            "security64@mail10.nospoofing.cn": "安全64战队",
            "security65@mail10.nospoofing.cn": "安全65战队",
            "security66@mail10.nospoofing.cn": "安全66战队",
            "security67@mail10.nospoofing.cn": "安全67战队",
            "security68@mail10.nospoofing.cn": "安全68战队",
            "security69@mail10.nospoofing.cn": "安全69战队",
            "security70@mail10.nospoofing.cn": "安全70战队",
            "security71@mail10.nospoofing.cn": "安全71战队",
            "security72@mail10.nospoofing.cn": "安全72战队",
            "security73@mail10.nospoofing.cn": "安全73战队",
            "security74@mail10.nospoofing.cn": "安全74战队",
            "security75@mail10.nospoofing.cn": "安全75战队",
            "security76@mail10.nospoofing.cn": "安全76战队",
            "security77@mail10.nospoofing.cn": "安全77战队",
            "security78@mail10.nospoofing.cn": "安全78战队",
            "security79@mail10.nospoofing.cn": "安全79战队",
            "security80@mail10.nospoofing.cn": "安全80战队",
            "security81@mail10.nospoofing.cn": "安全81战队",
            "security82@mail10.nospoofing.cn": "安全82战队",
            "security83@mail10.nospoofing.cn": "安全83战队",
            "security84@mail10.nospoofing.cn": "安全84战队",
            "security85@mail10.nospoofing.cn": "安全85战队",
            "security86@mail10.nospoofing.cn": "安全86战队",
            "security87@mail10.nospoofing.cn": "安全87战队",
            "security88@mail10.nospoofing.cn": "安全88战队",
            "security89@mail10.nospoofing.cn": "安全89战队",
            "security90@mail10.nospoofing.cn": "安全90战队",
            "security91@mail10.nospoofing.cn": "安全91战队",
            "security92@mail10.nospoofing.cn": "安全92战队",
            "security93@mail10.nospoofing.cn": "安全93战队",
            "security94@mail10.nospoofing.cn": "安全94战队",
            "security95@mail10.nospoofing.cn": "安全95战队",
            "security96@mail10.nospoofing.cn": "安全96战队",
            "security97@mail10.nospoofing.cn": "安全97战队",
            "security98@mail10.nospoofing.cn": "安全98战队",
            "security99@mail10.nospoofing.cn": "安全99战队",

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

    'red2': '\033[91m',
    'green2': '\033[92m',
    'yellow2': '\033[93m',
    'blue2': '\033[94m',
    'magenta2': '\033[95m',
    'cyan2': '\033[96m',
    'white2': '\033[97m',
    'bold2': '\033[1m',
    'italic2': '\033[3m',
    'underline2': '\033[4m',
    'inverse2': '\033[7m',
    'hidden2': '\033[8m',

    'red3': '\033[91m',
    'green3': '\033[92m',
    'yellow3': '\033[93m',
    'blue3': '\033[94m',
    'magenta3': '\033[95m',
    'cyan3': '\033[96m',
    'white3': '\033[97m',
    'bold3': '\033[1m',
    'italic3': '\033[3m',
    'underline3': '\033[4m',
    'inverse3': '\033[7m',
    'hidden3': '\033[8m',

    'red4': '\033[91m',
    'green4': '\033[92m',
    'yellow4': '\033[93m',
    'blue4': '\033[94m',
    'magenta4': '\033[95m',
    'cyan4': '\033[96m',
    'white4': '\033[97m',
    'bold4': '\033[1m',
    'italic4': '\033[3m',
    'underline4': '\033[4m',
    'inverse4': '\033[7m',
    'hidden4': '\033[8m',

    'red5': '\033[91m',
    'green5': '\033[92m',
    'yellow5': '\033[93m',
    'blue5': '\033[94m',
    'magenta5': '\033[95m',
    'cyan5': '\033[96m',
    'white5': '\033[97m',
    'bold5': '\033[1m',
    'italic5': '\033[3m',
    'underline5': '\033[4m',
    'inverse5': '\033[7m',
    'hidden5': '\033[8m',

    'red21': '\033[91m',
    'green21': '\033[92m',
    'yellow21': '\033[93m',
    'blue21': '\033[94m',
    'magenta21': '\033[95m',
    'cyan21': '\033[96m',
    'white21': '\033[97m',
    'bold21': '\033[1m',
    'italic21': '\033[3m',
    'underline21': '\033[4m',
    'inverse21': '\033[7m',
    'hidden21': '\033[8m',

    'red22': '\033[91m',
    'green22': '\033[92m',
    'yellow22': '\033[93m',
    'blue22': '\033[94m',
    'magenta22': '\033[95m',
    'cyan22': '\033[96m',
    'white22': '\033[97m',
    'bold22': '\033[1m',
    'italic22': '\033[3m',
    'underline22': '\033[4m',
    'inverse22': '\033[7m',
    'hidden22': '\033[8m',

    'red23': '\033[91m',
    'green23': '\033[92m',
    'yellow23': '\033[93m',
    'blue23': '\033[94m',
    'magenta23': '\033[95m',
    'cyan23': '\033[96m',
    'white23': '\033[97m',
    'bold23': '\033[1m',
    'italic23': '\033[3m',
    'underline23': '\033[4m',
    'inverse23': '\033[7m',
    'hidden23': '\033[8m',

    'red24': '\033[91m',
    'green24': '\033[92m',
    'yellow24': '\033[93m',
    'blue24': '\033[94m',
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
        # ("security@mail10.nospoofing.cn",  "4RGeu4YgR5F78idx"),#客户端密码
        # ("security1@mail10.nospoofing.cn", "WqpU8fPykBZa8Qh9"),
        # ("security2@mail10.nospoofing.cn", "RP9tWI3PjaZTfZav"),
        # ("security3@mail10.nospoofing.cn", "3cw2EMwqZuHfzf9e"),
        # ("security4@mail10.nospoofing.cn", "e9MjDw9w3aQRSyHX"),
        # ("security5@mail10.nospoofing.cn", "Ins8wSqiUTuiQWfF"),
        # ("security6@mail10.nospoofing.cn", "IdjXqQmfuYi4Qtmz"),
        # ("security7@mail10.nospoofing.cn", "KG9zb9FKZnuHx2P6"),
        # ("security8@mail10.nospoofing.cn", "TXkDg4RvFPHUzZCi"),
        # ("security9@mail10.nospoofing.cn", "s2rfxBuD5ZNB3RyT"),
        # ("security10@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security11@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security12@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security13@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security14@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security15@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security16@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security17@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security18@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security19@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security20@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security21@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security22@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security23@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security24@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security25@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security26@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security27@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security28@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security29@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security30@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security31@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security32@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security33@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security34@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security35@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security36@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security37@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security38@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security39@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security40@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security41@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security42@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security43@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security44@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security45@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security46@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security47@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security48@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security49@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security50@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security51@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security52@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security53@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security54@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security55@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security56@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security57@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security58@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security59@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security60@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security61@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security62@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security63@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security64@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security65@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security66@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security67@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security68@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security69@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security70@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security71@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security72@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security73@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security74@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security75@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security76@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security77@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security78@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security79@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security80@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security81@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security82@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security83@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security84@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security85@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security86@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security87@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security88@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security89@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security90@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security91@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security92@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security93@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security94@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security95@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security96@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security97@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security98@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security99@mail10.nospoofing.cn", "aaaAAA@@@"),

        #("test@mail10.nospoofing.cn", "123abc123"),
        ("security41@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security43@mail10.nospoofing.cn", "aaaAAA@@@"),
        # ("security44@mail10.nospoofing.cn", "aaaAAA@@@"),
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
