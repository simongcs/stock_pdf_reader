import os


def run():
    os.system("pytest --cov --cov-report term-missing")
