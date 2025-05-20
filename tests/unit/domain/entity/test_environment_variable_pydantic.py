import pytest
from pydantic import ValidationError
from ecs_taskdef.domain.entity.environment_variable import EnvironmentVariable


def test_environment_variable_validation_success():
    """Test successful validation of EnvironmentVariable."""
    # Valid initialization
    env_var = EnvironmentVariable(name="ENV_NAME", value="env_value")
    
    # Check proper field values
    assert env_var.name == "ENV_NAME"
    assert env_var.value == "env_value"


def test_environment_variable_validation_failure():
    """Test validation failures for EnvironmentVariable."""
    # Missing required fields
    with pytest.raises(ValidationError) as exc_info:
        EnvironmentVariable(name="ENV_NAME")  # missing value
    
    assert "value" in str(exc_info.value)
    
    with pytest.raises(ValidationError) as exc_info:
        EnvironmentVariable(value="env_value")  # missing name
    
    assert "name" in str(exc_info.value)


def test_environment_variable_serialization():
    """Test serialization of EnvironmentVariable."""
    env_var = EnvironmentVariable(name="ENV_NAME", value="env_value")
    
    # Test model_dump (dict conversion)
    env_dict = env_var.model_dump()
    assert isinstance(env_dict, dict)
    assert env_dict["name"] == "ENV_NAME"
    assert env_dict["value"] == "env_value"
    
    # Test model_dump with by_alias=True
    env_dict_alias = env_var.model_dump(by_alias=True)
    assert env_dict_alias["name"] == "ENV_NAME"
    assert env_dict_alias["value"] == "env_value"


def test_environment_variable_from_dict():
    """Test creating EnvironmentVariable objects from dictionary."""
    input_dict = {"ENV1": "value1", "ENV2": "value2"}
    env_vars = EnvironmentVariable.from_dict(input_dict)
    
    assert len(env_vars) == 2
    assert isinstance(env_vars[0], EnvironmentVariable)
    assert isinstance(env_vars[1], EnvironmentVariable)
    
    # Check that both variables were created properly
    names = {env.name for env in env_vars}
    values = {env.value for env in env_vars}
    
    assert names == {"ENV1", "ENV2"}
    assert values == {"value1", "value2"}


def test_environment_variable_type_conversion():
    """Test type conversion during initialization."""
    # Test with non-string values that should be converted to strings
    env_var = EnvironmentVariable(name="INT_VAR", value="123")
    assert env_var.value == "123"
    
    env_var = EnvironmentVariable(name="BOOL_VAR", value="True")
    assert env_var.value == "True"