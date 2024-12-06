# Python 3.11 이미지를 기반으로 사용
FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

## Python 패키지 설치를 위한 파일 복사
#COPY requirements.txt requirements.txt
#
## 종속성 설치
#RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 정적 파일 경로 노출 (optional)
EXPOSE 8000

# Gunicorn 실행 명령어
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "sigkihan.wsgi:application"]