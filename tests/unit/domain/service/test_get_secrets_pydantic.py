import json
from unittest.mock import MagicMock, patch

import pytest
from botocore.exceptions import ClientError

from ecs_taskdef.domain.service.get_secrets import SecretValue


def test_secret_value_instantiation():
    """Test SecretValue instantiation."""
    # Can instantiate without arguments
    secret = SecretValue()
    assert isinstance(secret, SecretValue)


@patch("boto3.session.Session")
def test_get_from_secrets_manager_success(mock_session):
    """Test get_from_secrets_manager method with successful API call."""
    # Setup mock
    mock_client = MagicMock()
    mock_session_instance = MagicMock()
    mock_session.return_value = mock_session_instance
    mock_session_instance.client.return_value = mock_client

    # Set up the mock response
    mock_secret_data = {"username": "admin", "password": "secret123"}
    mock_client.get_secret_value.return_value = {
        "SecretString": json.dumps(mock_secret_data),
        "ARN": "arn:aws:secretsmanager:us-east-1:123456789012:secret:my-secret-123abc",
    }

    # Create SecretValue and call the method
    secret = SecretValue()
    result = secret.get_from_secrets_manager("my-secret")

    # Verify results
    assert result == mock_secret_data
    mock_session_instance.client.assert_called_once_with(service_name="secretsmanager")
    mock_client.get_secret_value.assert_called_once_with(SecretId="my-secret")


@patch("boto3.session.Session")
def test_get_from_secrets_manager_failure(mock_session):
    """Test get_from_secrets_manager method with API failure."""
    # Setup mock to raise exception
    mock_client = MagicMock()
    mock_session_instance = MagicMock()
    mock_session.return_value = mock_session_instance
    mock_session_instance.client.return_value = mock_client

    mock_client.get_secret_value.side_effect = ClientError(
        {"Error": {"Code": "ResourceNotFoundException", "Message": "Secret not found"}}, "GetSecretValue"
    )

    # Create SecretValue and attempt to fetch
    secret = SecretValue()

    # Should raise the ClientError
    with pytest.raises(ClientError) as exc_info:
        secret.get_from_secrets_manager("non-existent-secret")

    assert "ResourceNotFoundException" in str(exc_info.value)
    mock_client.get_secret_value.assert_called_once_with(SecretId="non-existent-secret")


@patch("boto3.session.Session")
def test_json_parsing(mock_session):
    """Test JSON parsing in get_from_secrets_manager."""
    # Setup mock
    mock_client = MagicMock()
    mock_session_instance = MagicMock()
    mock_session.return_value = mock_session_instance
    mock_session_instance.client.return_value = mock_client

    # Test with complex JSON data
    complex_data = {
        "database": {"username": "admin", "password": "secret123", "host": "db.example.com", "port": 5432},
        "api": {"key": "api-key-value", "endpoint": "https://api.example.com"},
    }

    mock_client.get_secret_value.return_value = {
        "SecretString": json.dumps(complex_data),
        "ARN": "arn:aws:secretsmanager:us-east-1:123456789012:secret:my-secret-123abc",
    }

    # Create SecretValue and call the method
    secret = SecretValue()
    result = secret.get_from_secrets_manager("complex-secret")

    # Verify results
    assert result == complex_data
    assert result["database"]["username"] == "admin"
    assert result["database"]["password"] == "secret123"
    assert result["api"]["key"] == "api-key-value"
