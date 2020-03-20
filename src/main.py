#### SOOJLE Ver2 추천 뉴스피드 구현 코드
#### 해당 뉴스피드는 [회원 추천 뉴스피드]에 한함
#### 웹 시스템에서 일어나는 다른 과정은 스킵되어 있음

#---------------환경변수 접근용--------------#
from iml_util import (db, timer, IMLError, proj)
#---------------SOOJLE 라이브러리------------#
from FastText import get_doc_vector, vec_sim
#-------------------------------------------#
import numpy as np
from datetime import datetime
from operator import itemgetter




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
	if result is None: 
		raise IMLError("회원이 존재하지 않음")
	return result


# 사용자 태그 리스트와 카테고리별 태그들을 모아서
# 의미 유사도를 조사한 후, 반환
# 실제로 해당 연산은 미리 캐싱되어 있어야
# 하기 때문에 시간 측정에서 제외
def tag_sim_process(tags):
	if tags in [None,[]]: 
		raise IMLError("태그 데이터가 없음")

	# 사용자 태그로 사용자 태그 벡터 구하기
	user_tags = []
	for key,value in tags.items():
		user_tags += [key] * value
	user_vec = get_doc_vector(user_tags)

	# 각 카테고리 내의 태그로 카테고리별 태그 가져오기
	cate_list = db['SJ_CATEGORY'].find(
			{	
				"category_name":{
					"$nin":["미사용","예외"]
				}
			},
			{
				"tag":1,
				"category_name":1
			}
	)
	if cate_list == []: 
		raise IMLError("카테고리 접근 에러")

	# 사용자와 카테고리간 의미 유사도 분석하기
	# 각 카테고리별 유사도 정렬해서 반환
	cate_vec = []
	for cate in cate_list:
		vec = vec_sim(user_vec, get_doc_vector(cate['tag']))
		cate_vec += [(cate['category_name'],vec)]
	print(cate_vec)
	cate_vec = sorted(cate_vec, key=itemgetter(1), reverse = True)
	return cate_vec


# 후보군 선정 제 1안 선정
# 카테고리별로 균형있게 추출
@timer
def candidates_with_cagegory(user_info, cate_vec):
	post_list = []
	# 카테고리 정보 호출
	cate_list = db['SJ_CATEGORY'].find(
			{	
				"category_name":{
					"$nin":["미사용","예외"]
				}
			},
			{
				"info_num":1,
				"category_name":1
			}
	)

	# 카테고리를 순회하며 post_list에 총 데이터 축적
	# 각 카테고리별 유사도에 따라 가져오는 개수가 달라짐
	for cate in cate_list:
		post_list += list(db['posts'].find(
			{
				'end_date':{"$gt":datetime.now()},
				'info_num':{"$in":cate['info']}
			},
			proj
		))

	if post_list == []: 
		raise IMLError("후보군 포스트가 없음")
	return post_list

#--------------------------------------------------#

if __name__ == '__main__':
	user_info = get_userinfo("16011089")
	cate_vec = tag_sim_process(user_info['tag'])
	#post_list = candidates_with_cagegory(user_info, cate_vec)
	print(cate_vec)
	
