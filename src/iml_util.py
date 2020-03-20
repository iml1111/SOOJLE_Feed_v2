import sys
sys.path.insert(0,'../../')
sys.path.insert(0,'../../SJ_AI/src/')
sys.path.insert(0,'../../IML_Tokenizer/src/')
from DB_INFO import (HOST, ID, PW)
from pymongo import MongoClient
import datetime

# 모듈 시간 측정 데코레이터
def timer(f):
    def wrapper(*args, **kwargs):
        start_time = datetime.datetime.now()
        result = f(*args, **kwargs)
        end_time = datetime.datetime.now()
        print(f.__name__,"Time:",end_time-start_time,"sec")
        return result
    return wrapper


# DB 접근
# ID, PW, HOST는 깃폴더밖에서 DB_INFO를 따로 만들어야 함
client = MongoClient('mongodb://%s:%s@%s' %(ID, PW, HOST))
db = client['soojle']


# 에러 핸들러
class IMLError(Exception):
		def __init__(self, msg):
			self.msg = msg
		def __str__(self):
			return self.msg


# 몽고디비 쿼리 프로젝션
# 너무 길어서 여기로 옮겨둠
proj = {
            '_id': 1,
            'title': 1,
            'date': 1,
            'img': 1,
            'fav_cnt': 1,
            'view': 1,
            'url': 1,
            'title_token': 1,
            'info': 1,
            'tag': 1,
            'topic': 1,
            'ft_vector': 1,
            'end_date': 1
        }