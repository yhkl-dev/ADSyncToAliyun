# ADSyncToAliyun

### usage

```shell
pip install -r requirements 
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
docker build  . -t ad_sync_to_aliyun:v1
docker run -e "access_key_id=xxxx" -e "access_key_secret=xxxx" -e "hostname=xxxx" -e "username=xxxx" -e "password=xxxx" -e "domain=xxxx" -d ad_sync_to_aliyun:v1 
```