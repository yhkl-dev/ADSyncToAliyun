import json
import time
import os
from typing import Tuple

from alibabacloud_ram20150501 import models as ram_20150501_models
from alibabacloud_ram20150501.client import Client as Ram20150501Client
from alibabacloud_tea_openapi import models as open_api_models
from ldap3 import ALL, ALL_ATTRIBUTES, NTLM, Connection, Server

BLOCK_LIST = [
    "krbtgt",
    "Administrator",
    "Guest",
    "fsadmin",
    "DC",
]


class AD:
    def __init__(self,
                 host: str,
                 username: str,
                 password: str,
                 base_domain: str,
                 port: int = 389) -> None:

        server = Server(host, get_info=ALL)
        self.base_domain = base_domain
        self.conn = Connection(
            server=server,
            auto_bind=True,
            authentication=NTLM,  # 连接Windows AD需要配置此项
            read_only=False,  # 禁止修改数据：True
            user=username,  # 管理员账户
            password=password,
        )
        self.search_filter = '(objectclass=user)'  # 只获取【用户】对象
        self.ou_search_filter = '(objectclass=organizationalUnit)'  # 只获取【OU】对象

    def get_all_users(self):
        search_base = ",".join(
            ["dc={}".format(x) for x in self.base_domain.split('.')])
        self.conn.search(search_base=search_base,
                         search_filter=self.search_filter,
                         attributes=ALL_ATTRIBUTES)

        res = json.loads(self.conn.response_to_json())
        return [
            r for r in res.get('entries')
            if r.get('attributes').get('cn') not in BLOCK_LIST
        ]

    def get_ou_users(self):
        search_base = ",".join(
            ["dc={}".format(x) for x in self.base_domain.split('.')])
        self.conn.search(search_base=search_base,
                         search_filter=self.ou_search_filter,
                         attributes=ALL_ATTRIBUTES)

        return json.loads(self.conn.response_to_json())


class Aliyun:
    def __init__(self, access_key_id, access_key_secret, host, username,
                 password, base_domain) -> None:
        self.ad = AD(host, username, password, base_domain)
        self.client = self.create_client(access_key_id, access_key_secret)

    def create_client(
        self,
        access_key_id: str,
        access_key_secret: str,
    ) -> Ram20150501Client:
        """
        使用AK&SK初始化账号Client
        @param access_key_id:
        @param access_key_secret:
        @return: Client
        @throws Exception
        """
        config = open_api_models.Config(access_key_id=access_key_id,
                                        access_key_secret=access_key_secret)
        # 访问的域名
        config.endpoint = 'ram.aliyuncs.com'
        return Ram20150501Client(config)

    def list_all_ram_user(self) -> None:
        list_users_request = ram_20150501_models.ListUsersRequest()
        res = self.client.list_users(list_users_request)
        x = res.body.users.to_map()
        return x.get("User")

    def create_user(self, user_tuple: Tuple[str]) -> str:
        create_user_request = ram_20150501_models.CreateUserRequest(
            user_name=user_tuple[0], display_name=user_tuple[1])
        try:
            self.client.create_user(create_user_request)
            return None
        except Exception as e:
            return str(e)

    def delete_user(self, user_tuple: Tuple[str]) -> str:
        delete_user_request = ram_20150501_models.DeleteUserRequest(
            user_name=user_tuple[0])
        try:
            self.client.delete_user(delete_user_request)
            return None
        except Exception as e:
            return str(e)

    def sync(self):
        ad_list = [(u['attributes']['name'], u['attributes']['displayName'])
                   for u in self.ad.get_all_users()]
        ram_list = [(u.get("UserName"), u.get("DisplayName"))
                    for u in self.list_all_ram_user()]
        # 待创建用户列表
        create_list = list(set(ad_list) - set(ram_list))
        # 待删除用户列表
        delete_list = list(set(ram_list) - set(ad_list))

        create_res = list(map(self.create_user, create_list))
        print(create_res)
        delete_res = list(map(self.delete_user, delete_list))
        if len(create_res) == 0 and len(delete_res) == 0:
            print("sync done")
        else:
            print(create_res)
            print(delete_res)


if __name__ == "__main__":

    access_key_id = os.environ.get('access_key_id')
    access_key_secret = os.environ.get('access_key_secret')
    hostname = os.environ.get('hostname')
    username = os.environ.get('username')
    password = os.environ.get('password')
    domain = os.environ.get('domain')
    print(access_key_id)
    print(access_key_secret)
    print(hostname)
    print(username)
    print(password)
    print(domain)

    print("start")
    ali = Aliyun(access_key_id, access_key_secret, hostname, username,
                 password, domain)

    while True:
        ali.sync()
        time.sleep(60 * 60 * 4)
