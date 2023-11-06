# #*- coding:utf-8 -*-
# import subprocess
# import json
#
# # 读取包含域名列表的TXT文件
# with open('Tranco-top-10000-domain.txt', 'r') as file:
#     domains = file.read().splitlines()
#
# results = {}
#
# for domain in domains:
#     command = f'nslookup -type=txt _dmarc.{domain}.com'
#
#     try:
#         output = subprocess.check_output(command, shell=True, text=True)#subprocess.check_output()函数用于执行外部命令
#
#         start_index = output.find('v=DMARC1')
#         end_index = output.find('"', start_index)
#         dmarc_record = output[start_index:end_index]
#         results[domain] = dmarc_record
#         print(f'{domain}: {dmarc_record}')
#
#     except subprocess.CalledProcessError as e:
#         results[domain] = f'Error: {e.output}'
#
# print(results)
#
# with open('DMARC_TOP_10000_Output.txt', 'w') as outfile:
#     json.dump(results, outfile)

import dns.resolver

# 读取包含域名列表的TXT文件
with open('Tranco-top-10000-domains.txt', 'r') as file:
    domains = file.read().splitlines()

# 创建一个空字典来存储结果
results = {}

with open('DMARC_TOP_10000_Output.txt', 'w') as outfile:
    for domain in domains:
        try:
            dmarc_domain = f'_dmarc.{domain}'
            answers = dns.resolver.query(dmarc_domain, 'TXT')

            dmarc_record = str(answers[0].strings[0], 'utf-8')

            results[domain] = dmarc_record
            print(f'{domain}: {dmarc_record}')
            #写入json格式的{domain}: {dmarc_record}，类似{"google.com": "v=DMARC1; p=reject; rua=mailto:mailauth-reports@google.com"}
            outfile.write(f'{{"{domain}": "{dmarc_record}"}}\n')

        except Exception as e:
            # 如果查询失败，记录错误信息
            results[domain] = f'Error: {e}'




