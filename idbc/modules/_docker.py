import subprocess
import os


def start_postgres_docker():
    postgres_compose_up = ["docker-compose", "up", "-d"]
    postgres_compose_down = ["docker-compose", "down"]
    # os.chdir('iroha')
    postgres_up = subprocess.run(postgres_compose_up)


def start_consumer():
    consumer_up = ["./consumer.sh"]
    consumer_up = subprocess.run(consumer_up)
