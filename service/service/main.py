from pydantic import BaseSettings


class MeConfig(BaseSettings):
    bucket: str


def main(event, context):
    config = MeConfig()
    print(config.bucket)
