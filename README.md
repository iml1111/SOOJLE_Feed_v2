# SOOJLE_Feed_v2

기존 SOOJLE에서 사용해야 하는 외부 라이브러리를 기본으로 사용하므로 pip freeze 적용 X 
(추가적인 라이브러리가 몇개? 있을 수도 있음)

# 요구사항

- iml_util.py 내에 입력된 환경 변수 경로 내에서 db_info 파일을 만들어야 함.
```python
from db_info import (HOST, ID, PW)
```
- 마찬가지로 입력된 환경변수 경로에 딱 맞게 토크나이저랑 SJ_AI 모듈도 함께 있어야 함.


# 사용 방법
```python
> python main.py
```
