# Python 람다 함수를 위한 Dockerfile(Linux/ARM64)
FROM python:3.12
RUN echo "FROM complete"

# Poetry 설치
RUN pip install -U poetry
# RUN curl -sSL https://install.python-poetry.org | python3 -
RUN echo "poerty install complete"

# 경로 정의
WORKDIR /workdir
RUN echo "WORKDIR complete"

# 로컬에 있는 pyproject.toml, poetry.lock 파일을 컨테이너로 복사
COPY poetry.lock pyproject.toml /workdir/
RUN echo "COPY complete"

# Poetry를 이용하여 의존성 설치 
# RUN poetry install --no-root --no-interaction
RUN poetry config virtualenvs.create false \
 && poetry install --no-root --no-interaction 
RUN echo "poetry complete"

# 로컬에 있는 소스코드를 컨테이너로 복사
COPY . /workdir
RUN echo "COPY complete"

# Python 경로 설정
ENV PYTHONPATH=/usr/local/bin/python3.12
RUN echo "PYTHONPATH complete"

# Poetry 바이너리 권한 확인 및 설정
RUN chmod +x /usr/local/bin/poetry
RUN echo "chmod complete"

# Poetry가 설치된 Python을 사용하도록 설정
RUN sed -i '1s|^.*$|#!/usr/local/bin/python3.12|' /usr/local/bin/poetry
RUN echo "sed complete"

# 권한과 바이너리 위치 확인
RUN ls -l /usr/local/bin/poetry
RUN echo "poetry complete"

WORKDIR /workdir/app
RUN echo "WORKDIR complete"
CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
RUN echo "CMD complete"
