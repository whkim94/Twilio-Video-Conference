###########
# BUILDER #
###########

FROM python:3.8.1-alpine as builder

WORKDIR /usr/src/app

# set environment variables
ENV LANG    C.UTF-8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN apk add --virtual python3-dev libffi-dev jpeg-dev zlib-dev musl-dev cairo-dev cairo pango-dev gdk-pixbuf gcc \
    && apk add --no-cache mariadb-dev \
    && apk add --no-cache tzdata \
    && ln -sf /usr/share/zoneinfo/America/Los_Angeles /etc/localtime \
    && echo "America/Los_Angeles" > /etc/timezone

# install pip
RUN pip3 install --upgrade pip

COPY ./requirements.txt .
RUN pip3 wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt


#########
# FINAL #v
#########

FROM python:3.8.1-alpine

# create directory for the app user
RUN mkdir -p /home/app

# create the app user
RUN addgroup -S app && adduser -S app -G app

ENV LANG    C.UTF-8
# create the appropriate directories
ENV HOME=/home
ENV APP_HOME=/home/app
WORKDIR $APP_HOME

# install dependencies
RUN apk update
RUN apk add --virtual python3-dev libffi-dev jpeg-dev zlib-dev musl-dev cairo-dev cairo pango-dev gdk-pixbuf gcc \
    && apk add --no-cache mariadb-dev \
    && apk add --no-cache tzdata \
    && apk add --no-cache font-misc-misc \
    && ln -sf /usr/share/zoneinfo/America/Los_Angeles /etc/localtime \
    && echo "America/Los_Angeles" > /etc/timezone

RUN cd $HOME/..
RUN wget http://cdn.naver.com/naver/NanumFont/fontfiles/NanumFont_TTF_ALL.zip
RUN mkdir /usr/share/fonts/nanumfont
RUN unzip NanumFont_TTF_ALL.zip -d /usr/share/fonts/nanumfont/.

RUN fc-cache -f && rm -rf /var/cache/*

COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/requirements.txt .
RUN pip3 install --upgrade pip
RUN pip3 install --no-cache /wheels/*

# copy project
COPY . $APP_HOME

RUN chmod +x start.sh
# chown all the files to the app user
#RUN chown -R app:app $APP_HOME

USER root

# ENTRYPOINT ["/home/app/start.sh"]