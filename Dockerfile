FROM python:3.8
ENV PYTHONUNBUFFERED 1
RUN mkdir -p /project/summer

 # 设置容器内工作目录
WORKDIR /project/summer

 # 将当前目录文件拷贝一份到工作目录中（. 表示当前目录）
ADD . /project/summer

 # 利用 pip 安装依赖
RUN pip install -r requirements.txt
RUN chmod 777 /project/summer/media


ENV DB_USERNAME=root
ENV DB_PASSWORD=123456
ENV DB_HOST=localhost
ENV DB_PORT=3306
ENV DJANGO_DEBUG=False

# 暴露接口
EXPOSE 8000
EXPOSE 8001

# 运行数据库迁移并启动项目
CMD python manage.py makemigrations && python manage.py migrate && uwsgi --ini uwsgi.ini && daphne -b 0.0.0.0 -p 8001 summer_backend.asgi:application
