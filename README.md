## ADSyncToAliyun

#### usage

```shell
pip install -r requirements.txt 
export access_key_id=xxxx; 
export access_key_secret=xxxx; 
export hostname=xxxx; 
export username=xxx;
export password=xxxx;
export domain=xxxx;

python main.py
```

#### DOCKER 

```shell
cd ADSyncToAliyun
docker build  . -t ad_sync_to_aliyun:v1

docker run -e access_key_id="xxxxxx" -e access_key_secret="xxxx" -e hostname="xxxxxx" -e username=xxxxxx -e password=xxxxxx -e domain="xxxx"  ad_sync_to_aliyun:v1
```

#### 说明

默认四小时同步一次

#### 前提条件

+ 有AD域
+ aliyun配置了AD域
