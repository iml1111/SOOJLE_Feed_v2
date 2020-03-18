# 해당 뉴스피드는 회원 추천 뉴스피드에 한함
# 따라 토큰 전송을 비롯한 웹 시스템에서 일어나는 모든 과정 스킵

import sys
sys.path.insert(0,'../../')
from DB_INFO import (HOST, ID, PW)
from pymongo import MongoClient
import numpy as np

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

# 뉴스피드v2 코드 관련 영역
#--------------------------------------------------#
# 회원 정보 조회
def get_userinfo(user_id):
	result = db['SJ_USER'].find_one(
			{"user_id":user_id},
			{
				"topic":1,
				"tag":1,
				"ft_vector":1,
				"tag_sum":1,
				"measurement_num":1
			}
		)
	if result is None: raise IMLError("해당 회원이 존재하지 않음")
	return result

#--------------------------------------------------#

if __name__ == '__main__':
	user_info = get_userinfo(user_id = "16011089")
	