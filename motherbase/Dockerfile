FROM python:3.7

ENV PYTHONUNBUFFERED=1

COPY Pipfile /
COPY Pipfile.lock /
RUN pip install pipenv && pipenv install --system --deploy

COPY app /app
WORKDIR /


CMD ["python", "-m", "app"]