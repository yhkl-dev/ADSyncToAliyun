import json
import sys
from typing import List

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

    def get_out_users(self):
        search_base = ",".join(
            ["dc={}".format(x) for x in self.base_domain.split('.')])
        self.conn.search(search_base=search_base,
                         search_filter=self.ou_search_filter,
                         attributes=ALL_ATTRIBUTES)

        return json.loads(self.conn.response_to_json())


class Aliyun:
    def __init__(self, access_key, access_secret, host, username, password,
                 base_domain) -> None:
        self.access_key = access_key
        self.access_secret = access_secret
        self.ad = AD(host, username, password, base_domain)

    @staticmethod
    def create_client(
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
        config = open_api_models.Config(
            # 您的AccessKey ID,
            access_key_id=access_key_id,
            # 您的AccessKey Secret,
            access_key_secret=access_key_secret)
        # 访问的域名
        config.endpoint = 'ram.aliyuncs.com'
        return Ram20150501Client(config)

    @staticmethod
    def list_all_ram_user(args: List[str], ) -> None:
        client = Aliyun.create_client('accessKeyId', 'accessKeySecret')
        list_users_request = ram_20150501_models.ListUsersRequest()
        # 复制代码运行请自行打印 API 的返回值
        client.list_users(list_users_request)

    @staticmethod
    def main(args: List[str], ) -> None:
        client = Aliyun.create_client('accessKeyId', 'accessKeySecret')
        create_user_request = ram_20150501_models.CreateUserRequest(
            UserName="user2", DisplayName="user2")
        # 复制代码运行请自行打印 API 的返回值
        client.create_user(create_user_request)


if __name__ == "__main__":
    print("start")
