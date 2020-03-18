import sys
sys.path.insert(0,'../../')

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


#사용자 태그 관심도 사전 정의
# "신희재"가 현재 가지고 있는 관심태그임
# 제 1안, 카테고리별 후보군 선정을 위해 필요
# 실제 서비스에서는 이미 캐싱이 
# 되어있어야 했기 때문에 미리 연산해둠

