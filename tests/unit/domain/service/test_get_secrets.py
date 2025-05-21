import json
import unittest.mock as mock

from botocore.exceptions import ClientError

from ecs_taskdef.domain.service.get_secrets import SecretValue


def test_get_secrets_success():
    """Test successful retrieval of secrets from AWS Secrets Manager."""
    # Mock data
    secret_name = "test/secret"
    secret_data = {"key1": "value1", "key2": "value2"}
    mock_response = {"SecretString": json.dumps(secret_data)}

    # Create mock session and client
    with mock.patch("boto3.session.Session") as mock_session:
        mock_client = mock.MagicMock()
        mock_session.return_value.client.return_value = mock_client
        mock_client.get_secret_value.return_value = mock_response

        # Call the function
        secret_value = SecretValue()
        result = secret_value.get_from_secrets_manager(secret_name)

        # Assert
        mock_session.return_value.client.assert_called_once_with(service_name="secretsmanager")
        mock_client.get_secret_value.assert_called_once_with(SecretId=secret_name)
        assert result == secret_data


def test_get_secrets_error():
    """Test error handling when retrieving secrets from AWS Secrets Manager."""
    # Mock data
    secret_name = "test/secret"
    error_response = {
        "Error": {"Code": "ResourceNotFoundException", "Message": "Secrets Manager can't find the specified secret."}
    }
    client_error = ClientError(error_response, "GetSecretValue")

    # Create mock session and client
    with mock.patch("boto3.session.Session") as mock_session:
        mock_client = mock.MagicMock()
        mock_session.return_value.client.return_value = mock_client
        mock_client.get_secret_value.side_effect = client_error

        # Call the function and expect exception
        secret_value = SecretValue()
        try:
            secret_value.get_from_secrets_manager(secret_name)
            assert False, "Expected ClientError to be raised"
        except ClientError as e:
            # Verify the error is passed through
            assert e.response["Error"]["Code"] == "ResourceNotFoundException"
