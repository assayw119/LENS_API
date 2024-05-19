# Python 람다 함수를 위한 Dockerfile(Linux/ARM64)
FROM arm64v8/python:3.12

# Poetry 설치
RUN pip install -U poetry

# 경로 정의
WORKDIR /app

# 로컬에 있는 pyproject.toml, poetry.lock 파일을 컨테이너로 복사
COPY poetry.lock pyproject.toml /app/

# Poetry를 이용하여 의존성 설치
RUN poetry install --no-root --no-interaction

# 로컬에 있는 소스코드를 컨테이너로 복사
COPY . /app

# Python 경로 설정
# ENV PYTHONPATH=/app

CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
