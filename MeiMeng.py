import requests
import json
import random
import time
import threading
import re


class MeiMeng:
    def __init__(self):
        self.ua = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'
        self.cookie, self.token = self.login()
        self.headers = {
            'authorization': self.token,
            'cookie': self.cookie,
            'user-agent': self.ua
        }

    # 登录
    def login(self):
        url = 'https://www.clubmeitu.com/wp-json/jwt-auth/v1/token'
        headers = {
            'referer': 'https://www.clubmeitu.com/',
            'user-agent': self.ua
        }
        data = {
            'username': "11111", # 这里填用户名
            'password': "22222" # 这里填密码
        }
        result = session.post(url, headers=headers, data=data)
        cookie = result.headers['Set-Cookie'].split(';')[10][11:]
        result = json.loads(result.text)
        token = f"Bearer {result['token']}"
        return cookie, token

    def sign(self):
        url = 'https://www.clubmeitu.com/wp-json/b2/v1/userMission'
        result = session.post(url, headers=self.headers)
        print(result.text)

    # 签到
    def get_task_data(self):
        url = 'https://www.clubmeitu.com/wp-json/b2/v1/getTaskData'
        result = session.post(url, headers=self.headers)
        result = json.loads(result.text)
        return result

    # 自动回复3个帖子
    def comment(self):
        url = 'https://www.clubmeitu.com/wp-json/b2/v1/commentSubmit'
        comment_list = ['感谢楼主分享', '好人一生平安', '楼主幸苦了', '终于找到了', '感谢大佬分享']
        for i in range(3):
            post_result = self.get_task_data()
            post_id = post_result['task']['task_comment']['url'][26:-5]
            data = {
                'comment_post_ID': post_id,
                'author': '52loli',
                'comment': comment_list[random.randint(0, 4)],
                'comment_parent': '0'
            }
            result = session.post(url, headers=self.headers, data=data)
            print(result.text)
            if i == 2:
                return
            time.sleep(45)

    # 关注
    def follow(self):
        id_list = []
        ids_dict = {}
        c = 0
        reg = r'v-if="follow\[(\d+)\]'
        page_max_reg = r'/(\d+) 页'
        page_url = 'https://www.clubmeitu.com/?s=&type=user'
        result = session.get(page_url, self.headers)
        result = re.findall(page_max_reg, result.text)
        page_max = int(result[0])
        follow_url = 'https://www.clubmeitu.com/wp-json/b2/v1/AuthorFollow'
        check_url = 'https://www.clubmeitu.com/wp-json/b2/v1/checkFollowByids'
        for page in range(page_max):
            page += 1
            user_info_url = 'https://www.clubmeitu.com/page/' + str(page) + '?s&type=user'
            r = session.get(user_info_url, headers=self.headers)
            r = re.findall(reg, r.text)

            # 封装用户id进字典
            for j in r:
                ids_dict[f'ids[{c}]'] = j
                c += 1
            c = 0
            # 检测字典里的用户是否已关注
            check_list = session.post(check_url, headers=self.headers, data=ids_dict)
            check_list = json.loads(check_list.text)
            for tmp in check_list:
                if not check_list[tmp]:
                    id_list.append(tmp)
                    # 当列表里有3个用户ID就退出这一层循环
                    if len(id_list) == 3:
                        break
            # 同上
            if len(id_list) == 3:
                break
        # 关注用户
        for k in id_list:
            data = {
                'user_id': k
            }
            result = session.post(follow_url, headers=self.headers, data=data)
            print(result.text)
            time.sleep(1)


if __name__ == '__main__':
    session = requests.session()
    cos = MeiMeng()
    sign = threading.Thread(target=cos.sign)
    comment = threading.Thread(target=cos.comment)
    follow = threading.Thread(target=cos.follow)
    sign.start()
    comment.start()
    follow.start()
