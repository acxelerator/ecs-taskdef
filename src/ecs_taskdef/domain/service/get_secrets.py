import json

import boto3
from botocore.exceptions import ClientError
from ecs_taskdef.domain.entity.container_definition import Secrets


class SecretValue:
    def get_from_secrets_manager(self, secret_name: str) -> dict:
        session = boto3.session.Session()
        client = session.client(service_name="secretsmanager")

        try:
            get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        except ClientError as e:
            # For a list of exceptions thrown, see
            # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
            raise e

        secret = get_secret_value_response["SecretString"]
        return json.loads(secret)

    def get_as_secrets(self, secrets_manager_arn: str) -> list[dict]:
        secret_dict = self.get_from_secrets_manager(secret_name=secrets_manager_arn)
        result = []
        for k, v in secret_dict.items():
            result.append(Secrets(name=k, valueFrom=secrets_manager_arn))
        return result
