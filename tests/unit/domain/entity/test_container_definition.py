from ecs_taskdef.domain.entity.container_definition import (
    ContainerDefinition,
    LogConfiguration,
    PortMapping,
    MountPoint,
    DependsOn,
    VolumesFrom,
    ULimit,
    LogConfigurationOptions
)
from ecs_taskdef.domain.entity.environment_variable import EnvironmentVariable


def test_log_configuration_creation():
    """Test that LogConfiguration object can be created correctly."""
    log_config = LogConfiguration(
        logDriver="awslogs",
        options=LogConfigurationOptions(**{
            "awslogs-group": "test-group",
            "awslogs-region": "us-west-2",
            "awslogs-stream-prefix": "test"
        }),
        secretOptions=[]
    )
    
    assert log_config.log_driver == "awslogs"
    assert log_config.options.awslogs_group == "test-group"
    assert log_config.options.awslogs_region == "us-west-2"
    assert log_config.options.awslogs_stream_prefix == "test"
    assert log_config.secret_options == []


def test_log_configuration_generate():
    """Test that LogConfiguration.generate creates a proper LogConfiguration."""
    log_config = LogConfiguration.generate(
        group_name="test-group",
        stream_prefix="test",
        region="us-west-2"
    )
    
    assert log_config.log_driver == "awslogs"
    assert log_config.options.awslogs_group == "test-group"
    assert log_config.options.awslogs_region == "us-west-2"
    assert log_config.options.awslogs_stream_prefix == "test"
    assert log_config.secret_options == []


def test_port_mapping_creation():
    """Test that PortMapping can be created correctly."""
    port_mapping = PortMapping(
        containerPort=80,
        hostPort=8080,
        protocol="tcp"
    )
    
    assert port_mapping.container_port == 80
    assert port_mapping.host_port == 8080
    assert port_mapping.protocol == "tcp"


def test_container_definition_generate():
    """Test that ContainerDefinition.generate creates a proper ContainerDefinition."""
    env_vars = EnvironmentVariable.from_dict({"ENV1": "value1", "ENV2": "value2"})
    port_mappings = [
        PortMapping(containerPort=80, hostPort=80, protocol="tcp")
    ]
    log_config = LogConfiguration.generate(
        group_name="test-group",
        stream_prefix="test",
        region="us-west-2"
    )
    
    container_def = ContainerDefinition.generate(
        name="test-container",
        image="test-image:latest",
        cpu=256,
        memory_reservation=512,
        environment=env_vars,
        port_mappings=port_mappings,
        log_configuration=log_config,
        essential=True
    )
    
    assert container_def.name == "test-container"
    assert container_def.image == "test-image:latest"
    assert container_def.cpu == 256
    assert container_def.memory_reservation == 512
    assert len(container_def.environment) == 2
    assert len(container_def.port_mappings) == 1
    assert container_def.essential is True
    assert container_def.log_configuration.log_driver == "awslogs"