FROM python:3.8
ENV PYTHONUNBUFFERED 1
RUN mkdir -p /project/summer

 # 设置容器内工作目录
WORKDIR /project/summer

 # 将当前目录文件拷贝一份到工作目录中（. 表示当前目录）
ADD . /project/summer

 # 利用 pip 安装依赖
RUN pip install -r requirements.txt
# RUN chmod 777 /project/summer/media


ENV DATABASE_USER=root
ENV DATABASE_PASSWORD=123456
ENV DATABASE_HOST=localhost
ENV DATABASE_PORT=3306

# 暴露接口
EXPOSE 8000

# 运行数据库迁移并启动项目
CMD python manage.py makemigrations && python manage.py migrate && daphne -b 0.0.0.0 -p 8000 summer_backend.asgi:application
