
FROM python:3.13


WORKDIR /app


COPY ./requirements.txt /app/requirements.txt


RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt


COPY ./ /app


EXPOSE 8000


RUN chmod +x /app/entrypoint.sh


ENTRYPOINT ["/app/entrypoint.sh"]


CMD ["python", "/app/main.py"]