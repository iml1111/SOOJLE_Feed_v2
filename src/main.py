#### SOOJLE Ver2 추천 뉴스피드 구현 코드
#### 해당 뉴스피드는 [회원 추천 뉴스피드]에 한함
#### 웹 시스템에서 일어나는 다른 과정은 스킵되어 있음

#---------------환경변수 접근용--------------#
from iml_util import (db, timer, IMLError)
#-------------------------------------------#
from FastText import get_doc_vector, vec_sim
import numpy as np
from datetime import timedelta, datetime
from operator import itemgetter
import pandas as pd
import numpy as np
from numpy import dot
from numpy.linalg import norm
from pprint import pprint
import operator
import random

# 뉴스피드v2 코드 관련 영역
#--------------------------------------------------#
#--------------------------------------------------#

# 회원 정보 조회
@timer # 시간측정 데코레이터
def get_userinfo(user_id):
	result = db['SJ_USER'].find_one(
			{"user_id":user_id},
			{
				
				"topic":1,
				"tag":1,
				"ft_vector":1,
				# v2 뉴스피드일 경우, 
				# 아래 파라미터가 필요없어짐
				#"tag_sum":1,
				# "measurement_num":1 
			}
		)
	if result is None: 
		raise IMLError("회원이 존재하지 않음")
	return result

#--------------------------------------------------#
#--------------------------------------------------#

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
				"category_name":1,
				"info_num":1
			}
	)

	# 사용자와 카테고리간 의미 유사도 분석하기
	# 각 카테고리별 유사도 정렬해서 반환
	# 다음 함수에서 정렬된 순서대로 포스트 후보군을 가져오게 됨
	cate_vec = []
	for cate in cate_list:
		vec = vec_sim(user_vec, get_doc_vector(cate['tag']))
		cate_vec += [(cate['category_name'],vec,cate['info_num'])]
	cate_vec = sorted(cate_vec, key=itemgetter(1), reverse = True)
	return cate_vec

#--------------------------------------------------#
#--------------------------------------------------#

# 후보군 선정 제 1안 선정
# 카테고리별로 균형있게 추출
@timer
def get_candidates(user_info, cate_list):
	post_list = []

	# 모든 카테고리에서 기본적으로 최대 700개씩 가져옴
	# POST_WEIGHT 변수를 일정 퍼센트씩 낮추면서 곱하는 것으로
	# 각기 다른 개수의 후보군 추출
	POST_NUM = 500
	POST_WEIGHT = 150
	MINUS_WEIGHT = -75

	# 카테고리를 순회하며 post_list에 총 데이터 축적
	# 각 카테고리별 유사도에 따라 가져오는 개수가 달라짐
	print("\n# 후보군 추출 명단")
	for cate in cate_list:
		temp = list(db['posts'].find(
			#각 카테고리별로 2달 이내의 정해진 수 만큼 추출
			{ 
				'$and':[
					{'info_num':{"$in":cate[2]}},
					{'end_date':{"$gt":datetime.now()}},
					{'date': {'$gt': (datetime.now() - 
									timedelta(days = 60))}}
				]
			},
			#프로젝션
			{
            	'_id': 1,
            	'title': 1,
            	'date': 1,
            	'img': 1,
            	'fav_cnt': 1,
            	#'view': 1,
            	'url': 1,
            	#'title_token': 1,
            	#'info': 1,
            	'tag': 1,
            	'topic': 1,
            	'ft_vector': 1,
            	'end_date': 1,
            	"popularity":1,
        	}
		).sort([('date', -1)]).limit(int(POST_NUM + POST_WEIGHT)))
		post_list += [temp]
		POST_WEIGHT += MINUS_WEIGHT
		print(cate[0],":",len(temp))
	print()
	if post_list == []: 
		raise IMLError("후보군 포스트가 없음")
	return post_list

#--------------------------------------------------#
#--------------------------------------------------#

# 포스트 유사도 분석 및 랭킹
# 트랜드 스코어 연산은 없다고 가정
# (기존 방법을 채택하되, v2 설계는 적용)
def get_sim(USER, POST, avg_popular = 20):
	#TOS
	TOS = (dot(USER['topic'], POST['topic']) / 
			(USER['norm']) * norm(POST['topic']))
	#TAS
	TAS = len(set(POST['tag']) & USER['tag_set']) / 10
	if TAS > 1: TAS = 1	
	#FAS
	FAS = vec_sim(USER['ft_vector'], POST['ft_vector'])
	result = (TOS*1) + (TAS*1) + (FAS*1) 

	# IS
	week_count = ((datetime.now() - POST['date']) / 7).days + 1
	# 최종 유사도 스코어 결정
	if avg_popular < (POST['popularity'] / week_count):
		result *= 1.3

	# # Random
	# 랜덤을 제거하는게 결정사항은 아님, 주석으로 표시해둘 것
	result += np.random.random() * 1
		
	return result

@timer
def post_ranking(user, posts_list):
	# 연산을 위해 미리 캐싱해둠
	user['norm'] = (norm(user['topic']))
	user['tag_set'] = set(user['tag'].keys())
	# 관심도 구하기 + 정렬 후 반환
	for idx, posts in enumerate(posts_list):
		for post in posts:
			post['topic'] = get_sim(user, post)
			# 필요없는 칼럼 삭제 구문
			del post['ft_vector']
			del post['tag']
		posts_list[idx] = sorted(posts_list[idx], 
			key=operator.itemgetter('topic'), reverse=True)
	# 각 카테고리를 지정된 갯수만큼 자르기
	total_post_num = [80,32,32,32,20]
	for idx, _ in enumerate(posts_list):
		posts_list[idx] = posts_list[idx][:total_post_num[idx]]
	return posts_list

#--------------------------------------------------#
#--------------------------------------------------#

if __name__ == '__main__':
	user_info = get_userinfo("16011089")
	cate_list = tag_sim_process(user_info['tag'])
	candi_list = get_candidates(user_info, cate_list)
	post_list = post_ranking(user_info, candi_list)

	print("\n\n# 카테고리 최고 유사도")
	for posts in post_list:
		print(posts[0]['title'])
		print(posts[0]['topic'])
	print("\n# 카테고리별 평균 유사도")
	avg_sims = [0,0,0,0,0]
	for idx,posts in enumerate(post_list):
		for post in posts:
			avg_sims[idx] += post['topic']
		avg_sims[idx] /= len(posts)
		print(avg_sims[idx])

	print("\n\n# 뉴스피드 테스트 상단 20개")
	# 실제 셔플은 프론트단에서 
	# 수행해야 하므로 시간측정 X
	result = []
	for posts in post_list:
		result += posts
	random.shuffle(result)
	for post in result[:20]:
		print("#--------------------------#")
		print(post['title'])
		print(post['date'], "Like:" ,post['fav_cnt']) 
	
	

# #Pandas 정렬
# @timer
# def post_ranking_with_pandas(user, post_list):

# 	# 한주동안 평균 인기도(가정)
# 	# 해당 데이터도 캐싱되있어야 함
# 	avg_popular = 20
# 	# 연산을 위해 미리 캐싱해둠
# 	norm_user = (norm(user['topic']))
# 	tag_user = set(user['tag'].keys())
# 	post_list = pd.DataFrame(post_list)
# 	#최대 태그 가중치 제한 점수
# 	max_tag_num = 10
# 	# 평균 인기도 이상시의 가중치
# 	popular_point = 1.3

# 	post_list['sim'] = 0.0
# 	# TOS 계산
# 	post_list['sim'] += post_list.apply(
# 	lambda x: (dot(x['topic'],user['topic']) / 
# 		(norm_user * norm(x['topic']))), axis = 1)
	
# 	# TAS 계산
# 	post_list['tag'] = post_list .apply(
# 			lambda x: len(set(x['tag']) & tag_user),axis = 1)
# 	post_list.loc[
# 			post_list['tag'] > max_tag_num, 'tag'
# 		] = max_tag_num
# 	post_list['sim'] += (post_list['tag'] / max_tag_num)
	
# 	# FAS 계산
# 	post_list['sim'] += post_list.apply(
# 	lambda x: dot(x['ft_vector'],user['ft_vector']), axis = 1)
	
# 	# IS 계산 (기존의 점수 전체 가중)
# 	month_count = ((datetime.now() - post_list['date'])/7 +timedelta(days = 1)).dt.days
# 	post_list.loc[
# 			((post_list['popularity'] / month_count) >= 
# 				avg_popular), 'sim'
# 		] *= popular_point

# 	# RANDOM 가중치 계산
# 	post_list['sim'] += np.random.random(len(post_list))*3
	
# 	#유사도에 따른 정렬
# 	post_list = post_list.sort_values(by=['sim'], 
# 						axis=0, ascending=False)
# 	post_list['_id'] = post_list['_id'].astype(str)
# 	#post_list['date'] = post_list['date'].astype(str)
# 	#return post_list.to_json(orient='records')
# 	return post_list
