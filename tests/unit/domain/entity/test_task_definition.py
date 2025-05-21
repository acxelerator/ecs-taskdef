from ecs_taskdef.domain.entity.container_definition import (
    ContainerDefinition,
    LogConfiguration,
    PortMapping,
)
from ecs_taskdef.domain.entity.environment_variable import EnvironmentVariable
from ecs_taskdef.domain.entity.task_definition import (
    RuntimePlatform,
    Tag,
    TaskDefinition,
    Volumes,
    VolumesHost,
)


def test_runtime_platform_creation():
    """Test that a RuntimePlatform can be created correctly."""
    platform = RuntimePlatform(cpuArchitecture="ARM64")

    assert platform.cpu_architecture == "ARM64"


def test_tag_creation():
    """Test that a Tag can be created correctly."""
    tag = Tag(key="Environment", value="Production")

    assert tag.key == "Environment"
    assert tag.value == "Production"


def test_volumes_creation():
    """Test that Volumes can be created correctly."""
    host = VolumesHost(sourcePath="/path/to/host")
    volumes = Volumes(name="data", host=host)

    assert volumes.name == "data"
    assert volumes.host.source_path == "/path/to/host"


def test_volumes_generate_host():
    """Test that Volumes.generate_host creates volumes correctly."""
    volumes = Volumes.generate_host("data", "/path/to/host")

    assert volumes.name == "data"
    assert volumes.host.source_path == "/path/to/host"


def test_task_definition_generate():
    """Test that TaskDefinition.generate creates a task definition correctly."""
    # Create container definition
    env_vars = EnvironmentVariable.from_dict({"ENV1": "value1", "ENV2": "value2"})
    port_mappings = [PortMapping(containerPort=80, hostPort=80, protocol="tcp")]
    log_config = LogConfiguration.generate(group_name="test-group", stream_prefix="test", region="us-west-2")

    container_def = ContainerDefinition.generate(
        name="test-container",
        image="test-image:latest",
        cpu=256,
        memory_reservation=512,
        environment=env_vars,
        port_mappings=port_mappings,
        log_configuration=log_config,
    )

    # Create task definition
    tags = [Tag(key="Environment", value="Test")]
    volumes = [Volumes.generate_host("data", "/path/to/host")]

    task_def = TaskDefinition.generate(
        container_definitions=[container_def],
        family="test-family",
        task_role_arn="arn:aws:iam::123456789012:role/test-task-role",
        execution_role_arn="arn:aws:iam::123456789012:role/test-execution-role",
        cpu="1024",
        memory="2048",
        cpu_architecture="ARM64",
        tags=tags,
        volumes=volumes,
    )

    # Verify task definition properties
    assert task_def.family == "test-family"
    assert task_def.task_role_arn == "arn:aws:iam::123456789012:role/test-task-role"
    assert task_def.execution_role_arn == "arn:aws:iam::123456789012:role/test-execution-role"
    assert task_def.cpu == "1024"
    assert task_def.memory == "2048"
    assert task_def.runtime_platform.cpu_architecture == "ARM64"
    assert len(task_def.container_definitions) == 1
    assert task_def.container_definitions[0].name == "test-container"
    assert len(task_def.volumes) == 1
    assert task_def.volumes[0].name == "data"
    assert task_def.enable_fault_injection is False


def test_get_container_definition_by_name():
    """Test getting a container definition by name."""
    # Create container definitions
    log_config = LogConfiguration.generate(group_name="test-group", stream_prefix="test", region="us-west-2")

    container_def1 = ContainerDefinition.generate(
        name="container1",
        image="image1:latest",
        cpu=256,
        memory_reservation=512,
        environment=[],
        port_mappings=[],
        log_configuration=log_config,
    )

    container_def2 = ContainerDefinition.generate(
        name="container2",
        image="image2:latest",
        cpu=128,
        memory_reservation=256,
        environment=[],
        port_mappings=[],
        log_configuration=log_config,
    )

    # Create task definition
    task_def = TaskDefinition.generate(
        container_definitions=[container_def1, container_def2],
        family="test-family",
        task_role_arn="arn:aws:iam::123456789012:role/test-task-role",
        execution_role_arn="arn:aws:iam::123456789012:role/test-execution-role",
        cpu="1024",
        memory="2048",
        cpu_architecture="ARM64",
        tags=[],
    )

    # Get container by name
    container = task_def.get_container_definition_by_name("container1")
    assert container is not None
    assert container.name == "container1"
    assert container.image == "image1:latest"

    # Get non-existent container
    container = task_def.get_container_definition_by_name("nonexistent")
    assert container is None


def test_update_container_definition_by_name():
    """Test updating a container definition by name."""
    # Create container definitions
    log_config = LogConfiguration.generate(group_name="test-group", stream_prefix="test", region="us-west-2")

    container_def1 = ContainerDefinition.generate(
        name="container1",
        image="image1:latest",
        cpu=256,
        memory_reservation=512,
        environment=[],
        port_mappings=[],
        log_configuration=log_config,
    )

    # Create task definition
    task_def = TaskDefinition.generate(
        container_definitions=[container_def1],
        family="test-family",
        task_role_arn="arn:aws:iam::123456789012:role/test-task-role",
        execution_role_arn="arn:aws:iam::123456789012:role/test-execution-role",
        cpu="1024",
        memory="2048",
        cpu_architecture="ARM64",
        tags=[],
    )

    # Create updated container definition
    updated_container = ContainerDefinition.generate(
        name="container1",
        image="image1:updated",
        cpu=512,
        memory_reservation=1024,
        environment=[],
        port_mappings=[],
        log_configuration=log_config,
    )

    # Update the container definition
    task_def = task_def.update_container_definition_by_name("container1", updated_container)

    # Verify the update worked
    container = task_def.get_container_definition_by_name("container1")
    assert container is not None
    assert container.image == "image1:updated"
    assert container.cpu == 512
    assert container.memory_reservation == 1024


def test_export():
    """Test that export method works correctly."""
    # Create container definition
    log_config = LogConfiguration.generate(group_name="test-group", stream_prefix="test", region="us-west-2")

    container_def = ContainerDefinition.generate(
        name="test-container",
        image="test-image:latest",
        cpu=256,
        memory_reservation=512,
        environment=[],
        port_mappings=[],
        log_configuration=log_config,
    )

    # Create task definition
    task_def = TaskDefinition.generate(
        container_definitions=[container_def],
        family="test-family",
        task_role_arn="arn:aws:iam::123456789012:role/test-task-role",
        execution_role_arn="arn:aws:iam::123456789012:role/test-execution-role",
        cpu="1024",
        memory="2048",
        cpu_architecture="ARM64",
        tags=[Tag(key="Environment", value="Test")],
    )

    # Export the task definition
    result = task_def.export()

    # Verify export excludes specified fields
    assert "taskDefinitionArn" not in result
    assert "requires_attributes" not in result
    assert "compatibilities" not in result
    assert "revision" not in result

    # Verify correct attribute names are used (camelCase)
    assert "family" in result
    assert "containerDefinitions" in result
    assert "taskRoleArn" in result
    assert "executionRoleArn" in result
