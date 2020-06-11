FROM jjanzic/docker-python3-opencv

EXPOSE 5000

WORKDIR /code

ENV FLASK_APP camera_website.py
ENV FLASK_RUN_HOST 0.0.0.0
ENV SECRET_KEY Trash_Buffé

RUN apt-get install gcc 
COPY requirements.txt requirements.txt

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
ENV PYTHONPATH /code/app

COPY . .
# RUN flask db init
# RUN flask db migrate -m "users table"
# RUN flask db upgrade
CMD ["flask", "run"]