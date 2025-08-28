FROM python:3.12.6
RUN mkdir /auth_app
WORKDIR /auth_app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt
COPY . .
RUN chmod a+x ./entry/app-entry.sh
