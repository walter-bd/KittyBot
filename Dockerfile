FROM python:3.10
ARG UID=1001
ARG GID=1001
RUN apt update -y && apt upgrade -y \
    && apt install libfreetype6-dev libxft-dev fortune -y
COPY requirements.txt /home
RUN pip install -r /home/requirements.txt
RUN pip install https://github.com/lucasalberto01/chatterbot-pro/archive/refs/heads/master.zip
RUN python -m spacy download en_core_web_sm
COPY --chown=$UID:$GID . /home/
RUN mkdir /data  && chown -R $UID:$GID /data
ENV HOME /home
ENV FORTUNE_DIRECTORY /usr/share/games/fortunes
ENV KITTY_DB /data/persist.sqlite
WORKDIR /home
USER $UID
CMD ["python", "bot.py"]
