from ecs_taskdef.domain.entity.environment_variable import EnvironmentVariable


def test_environment_variable_creation():
    """Test that an environment variable can be created correctly."""
    env_var = EnvironmentVariable(name="MY_VAR", value="my_value")

    assert env_var.name == "MY_VAR"
    assert env_var.value == "my_value"


def test_from_dict():
    """Test that environment variables can be created from a dictionary."""
    env_dict = {"VAR1": "value1", "VAR2": "value2", "VAR3": "value3"}

    env_vars = EnvironmentVariable.from_dict(env_dict)

    assert len(env_vars) == 3

    # Test each environment variable
    assert any(ev.name == "VAR1" and ev.value == "value1" for ev in env_vars)
    assert any(ev.name == "VAR2" and ev.value == "value2" for ev in env_vars)
    assert any(ev.name == "VAR3" and ev.value == "value3" for ev in env_vars)


def test_from_dict_empty():
    """Test that from_dict handles empty dictionaries correctly."""
    env_dict = {}

    env_vars = EnvironmentVariable.from_dict(env_dict)

    assert len(env_vars) == 0
    assert isinstance(env_vars, list)
