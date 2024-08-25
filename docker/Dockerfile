FROM python:3.11.9-bookworm

ENV APP_HOME=/srv/message-queue
ENV VENV_PATH=${APP_HOME}/.venv
ENV PATH=${VENV_PATH}/bin:${PATH}

WORKDIR ${APP_HOME}

COPY pyproject.toml .

RUN pip install --upgrade pip && \
	pip install --no-cache uv && \
	mkdir .venv && \
	uv venv .venv && \
	uv pip install --no-cache .

COPY . ${APP_HOME}/

CMD ["python", "src/scheduler.py"]
