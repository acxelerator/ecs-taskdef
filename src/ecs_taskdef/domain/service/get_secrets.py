import json

import boto3
from botocore.exceptions import ClientError


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
