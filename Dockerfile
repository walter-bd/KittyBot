FROM python:3.10
ARG UID=1001
ARG GID=1001
RUN apt update -y && apt upgrade -y \
    && apt install libfreetype6-dev libxft-dev fortune -y
COPY requirements.txt /home
RUN pip install -r /home/requirements.txt
COPY --chown=$UID:$GID . /home/
RUN mkdir /data  && chown -R $UID:$GID /data
RUN mkdir -p /home/.cache && chown -R $UID:$GID /home/.cache
ENV HOME /home
ENV FORTUNE_DIRECTORY /usr/share/games/fortunes
ENV KITTY_DB /data/persist.sqlite
WORKDIR /home
USER $UID
CMD ["python", "bot.py"]
