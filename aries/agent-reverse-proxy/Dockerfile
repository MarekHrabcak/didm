FROM python:3.10.13-alpine

# RUN whoami
ADD . .

RUN apk --update --upgrade add gcc musl-dev jpeg-dev zlib-dev libffi-dev cairo-dev pango-dev gdk-pixbuf-dev
RUN pip3 install -r requirements.txt

RUN which sleep

EXPOSE 8080

CMD ["/usr/local/bin/hypercorn", "-b", "0.0.0.0:8080", "reverse_proxy.app:app"]
