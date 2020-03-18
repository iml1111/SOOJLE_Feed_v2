# SOOJLE Ver2 추천 뉴스피드 구현 코드
# 해당 뉴스피드는 [회원 추천 뉴스피드]에 한함
# 웹 시스템에서 일어나는 다른 과정은 스킵되어 있음
from iml_util import (db, timer, 
						IMLError, tag_vec)
from DB_INFO import (HOST, ID, PW)
from pymongo import MongoClient
import numpy as np
from datetime import datetime


# 뉴스피드v2 코드 관련 영역
#--------------------------------------------------#
# 회원 정보 조회
@timer # 시간측정 데코레이터
def get_userinfo(user_id):
	result = db['SJ_USER'].find_one(
			{"user_id":user_id},
			{
				# v2 뉴스피드일 경우, 
				# 다음과 같은 파라미터가 필요없어짐
				"topic":1,
				"tag":1,
				"ft_vector":1,
				# "tag_sum":1,
				# "measurement_num":1 
			}
		)
	if result is None: raise IMLError("회원이 존재하지 않음")
	return result

def tag_sim_process(tags):
	if tags in [None,[]]: 
		raise IMLError("태그 데이터가 없음")
	# 사용자 태그로 사용자 태그 벡터 구하기
	user_tags = []
	for key,value in tags.items():
		user_tags += [key] * value
	# 각 카테고리 내의 태그로 카테고리별 벡터 구하기
	cate_tags = {}
	db



# 후보군 선정 제 1안
# 카테고리별로 균형있게 추출
@timer
def get_posts_with_cagegory(user_info):
	post_list = list(db['posts'].find(
		{
			'end_date':{"$gt":datetime.now()}
		},
		{
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
	))

	if post_list == []: raise IMLError("후보군 포스트가 없음")
	return post_list

#--------------------------------------------------#

if __name__ == '__main__':
	user_info = get_userinfo("16011089")
	tag_vec, cate_vec = tag_sim_process(user_info['tag'])
	post_list = get_posts_with_cagegory(user_info)
	
