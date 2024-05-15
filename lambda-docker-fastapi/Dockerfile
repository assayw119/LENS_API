# Python 람다 함수를 위한 Dockerfile(Linux/ARM64)
FROM python:3.9.6

# Poetry 버전 정의
ENV POETRY_VERSION=1.8.3

# Poetry 설치
RUN pip install "poetry==$POETRY_VERSION"

# 경로 정의
WORKDIR /lambda-docker-fastapi/app

# 로컬에 있는 pyproject.toml, poetry.lock 파일을 컨테이너로 복사
COPY poetry.lock pyproject.toml /lambda-docker-fastapi/

# Poetry를 이용하여 의존성 설치
RUN poetry install --no-root --no-interaction --no-ansi --no-cache

# 로컬에 있는 소스코드를 컨테이너로 복사
COPY app /lambda-docker-fastapi/app/

# Python 경로 설정
ENV PYTHONPATH=/lambda-docker-fastapi

CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
