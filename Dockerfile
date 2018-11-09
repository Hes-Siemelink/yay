FROM python:3.6-stretch

COPY . /yay

WORKDIR /yay

RUN rm dist/*
RUN python setup.py bdist_wheel
RUN pip install dist/*.whl
RUN yay example/Hello.yay