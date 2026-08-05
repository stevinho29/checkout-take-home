FROM python:3.13-slim

ARG APP_NAME
ENV APP_NAME=${APP_NAME}
ENV APP_PATH=/usr/local/${APP_NAME}
ENV LOG_PATH=/var/log/${APP_NAME}

WORKDIR $APP_PATH
COPY pyproject.toml poetry.lock README.md .
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-root

COPY ./payment_gateway_api ./payment_gateway_api


CMD ["uvicorn", "payment_gateway_api.app:app", "--host", "0.0.0.0", "--port", "8081"]