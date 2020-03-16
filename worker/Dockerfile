FROM python
WORKDIR /app

COPY ./requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir

RUN apt-get update && apt-get install cron -y

COPY . .

ENTRYPOINT ["./entrypoint.sh"]