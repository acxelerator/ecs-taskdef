import pytest
from pydantic import ValidationError
from ecs_taskdef.domain.entity.container_definition import (
    ContainerDefinition,
    LogConfiguration,
    PortMapping,
    LogConfigurationOptions,
    ULimit,
    MountPoint,
    DependsOn,
    VolumesFrom,
    Secrets
)
from ecs_taskdef.domain.entity.environment_variable import EnvironmentVariable


def test_port_mapping_validation():
    """Test PortMapping validation with valid and invalid data."""
    # Valid data
    valid_port = PortMapping(containerPort=80, hostPort=8080, protocol="tcp")
    assert valid_port.container_port == 80
    assert valid_port.host_port == 8080
    assert valid_port.protocol == "tcp"
    
    # Testing protocol validation (must be tcp or udp)
    with pytest.raises(ValidationError) as exc_info:
        PortMapping(containerPort=80, hostPort=8080, protocol="invalid")
    
    assert "protocol" in str(exc_info.value)
    
    # Protocol is required
    with pytest.raises(ValidationError) as exc_info:
        PortMapping(containerPort=80, hostPort=8080)
    
    assert "protocol" in str(exc_info.value)
    
    # Serialization with aliases
    port_dict = valid_port.model_dump(by_alias=True)
    assert port_dict["containerPort"] == 80
    assert port_dict["hostPort"] == 8080
    assert port_dict["protocol"] == "tcp"


def test_ulimit_validation():
    """Test ULimit validation with valid and invalid data."""
    # Valid data
    ulimit = ULimit(name="nofile", softLimit=1024, hardLimit=2048)
    assert ulimit.name == "nofile"
    assert ulimit.soft_limit == 1024
    assert ulimit.hard_limit == 2048
    
    # Missing required fields
    with pytest.raises(ValidationError) as exc_info:
        ULimit(name="nofile", softLimit=1024)  # Missing hardLimit
    
    assert "hardLimit" in str(exc_info.value)
    
    # Alias field serialization
    ulimit_dict = ulimit.model_dump(by_alias=True)
    assert ulimit_dict["name"] == "nofile"
    assert ulimit_dict["softLimit"] == 1024
    assert ulimit_dict["hardLimit"] == 2048


def test_mount_point_validation():
    """Test MountPoint validation with valid and invalid data."""
    # Valid data
    mount_point = MountPoint(sourceVolume="data", containerPath="/data", readOnly=True)
    assert mount_point.source_volume == "data"
    assert mount_point.container_path == "/data"
    assert mount_point.read_only is True
    
    # read_only is required
    with pytest.raises(ValidationError) as exc_info:
        MountPoint(sourceVolume="data", containerPath="/data")
    
    assert "readOnly" in str(exc_info.value)
    
    # Alias field serialization
    mount_dict = mount_point.model_dump(by_alias=True)
    assert mount_dict["sourceVolume"] == "data"
    assert mount_dict["containerPath"] == "/data"
    assert mount_dict["readOnly"] is True


def test_log_config_options_validation():
    """Test LogConfigurationOptions validation."""
    # Valid data
    log_opts = LogConfigurationOptions(**{
        "awslogs-group": "my-group",
        "awslogs-region": "us-east-1",
        "awslogs-stream-prefix": "prefix"
    })
    
    assert log_opts.awslogs_group == "my-group"
    assert log_opts.awslogs_region == "us-east-1"
    assert log_opts.awslogs_stream_prefix == "prefix"
    
    # Serialization with aliases
    opts_dict = log_opts.model_dump(by_alias=True)
    assert opts_dict["awslogs-group"] == "my-group"
    assert opts_dict["awslogs-region"] == "us-east-1"
    assert opts_dict["awslogs-stream-prefix"] == "prefix"


def test_depends_on_validation():
    """Test DependsOn validation with valid and invalid data."""
    # Valid data
    depends = DependsOn(condition="START", containerName="web")
    assert depends.condition == "START"
    assert depends.container_name == "web"
    
    # Invalid condition value
    with pytest.raises(ValidationError) as exc_info:
        DependsOn(condition="INVALID", containerName="web")
    
    assert "condition" in str(exc_info.value)
    
    # Missing required fields
    with pytest.raises(ValidationError) as exc_info:
        DependsOn(condition="START")  # Missing containerName
    
    assert "containerName" in str(exc_info.value)


def test_volumes_from_validation():
    """Test VolumesFrom validation."""
    # Valid data
    volume = VolumesFrom(readOnly=True, sourceContainer="db")
    assert volume.read_only is True
    assert volume.source_container == "db"
    
    # Serialization with aliases
    vol_dict = volume.model_dump(by_alias=True)
    assert vol_dict["readOnly"] is True
    assert vol_dict["sourceContainer"] == "db"


def test_secrets_validation():
    """Test Secrets validation."""
    # Valid data
    secret = Secrets(name="DB_PASSWORD", valueFrom="arn:aws:secretsmanager:...")
    assert secret.name == "DB_PASSWORD"
    assert secret.value_from == "arn:aws:secretsmanager:..."
    
    # Serialization with aliases
    secret_dict = secret.model_dump(by_alias=True)
    assert secret_dict["name"] == "DB_PASSWORD"
    assert secret_dict["valueFrom"] == "arn:aws:secretsmanager:..."


def test_log_configuration_validation():
    """Test LogConfiguration validation."""
    # Valid data
    options = LogConfigurationOptions(**{
        "awslogs-group": "my-group",
        "awslogs-region": "us-east-1",
        "awslogs-stream-prefix": "prefix"
    })
    
    log_config = LogConfiguration(
        logDriver="awslogs",
        options=options,
        secretOptions=[]
    )
    
    assert log_config.log_driver == "awslogs"
    assert log_config.options.awslogs_group == "my-group"
    assert log_config.secret_options == []
    
    # Test serialization with aliases
    log_dict = log_config.model_dump(by_alias=True)
    assert log_dict["logDriver"] == "awslogs"
    assert isinstance(log_dict["options"], dict)
    assert log_dict["options"]["awslogs-group"] == "my-group"
    assert log_dict["secretOptions"] == []


def test_container_definition_validation():
    """Test ContainerDefinition validation with valid and invalid data."""
    # Prepare test data
    env_vars = [EnvironmentVariable(name="ENV1", value="value1")]
    port_mappings = [PortMapping(containerPort=80, hostPort=8080, protocol="tcp")]
    log_options = LogConfigurationOptions(**{
        "awslogs-group": "my-group",
        "awslogs-region": "us-east-1",
        "awslogs-stream-prefix": "prefix"
    })
    log_config = LogConfiguration(
        logDriver="awslogs",
        options=log_options,
        secretOptions=[]
    )
    depends_on = [DependsOn(condition="START", containerName="db")]
    
    # Valid container definition
    container = ContainerDefinition(
        name="web",
        image="nginx:latest",
        cpu=256,
        memoryReservation=512,
        portMappings=port_mappings,
        essential=True,
        environment=env_vars,
        environmentFiles=[],
        mountPoints=[],
        volumesFrom=[],
        dnsServers=[],
        dnsSearchDomains=[],
        extraHosts=[],
        dockerSecurityOptions=[],
        dependsOn=depends_on,
        logConfiguration=log_config,
        systemControls=[]
    )
    
    assert container.name == "web"
    assert container.image == "nginx:latest"
    assert container.cpu == 256
    assert container.memory_reservation == 512
    assert container.essential is True
    assert len(container.environment) == 1
    assert container.environment[0].name == "ENV1"
    
    # Test serialization with aliases
    container_dict = container.model_dump(by_alias=True)
    assert container_dict["name"] == "web"
    assert container_dict["image"] == "nginx:latest"
    assert container_dict["cpu"] == 256
    assert container_dict["memoryReservation"] == 512
    assert container_dict["essential"] is True
    assert isinstance(container_dict["portMappings"], list)
    assert isinstance(container_dict["environment"], list)
    assert container_dict["environment"][0]["name"] == "ENV1"


def test_container_definition_required_fields():
    """Test ContainerDefinition required field validation."""
    # Missing required fields
    log_options = LogConfigurationOptions(**{
        "awslogs-group": "my-group",
        "awslogs-region": "us-east-1",
        "awslogs-stream-prefix": "prefix"
    })
    log_config = LogConfiguration(
        logDriver="awslogs",
        options=log_options,
        secretOptions=[]
    )
    depends_on = [DependsOn(condition="START", containerName="db")]
    
    # Missing required fields
    with pytest.raises(ValidationError) as exc_info:
        ContainerDefinition(
            name="web",
            # Missing image
            cpu=256,
            memoryReservation=512,
            portMappings=[],
            essential=True,
            environmentFiles=[],
            dnsServers=[],
            dnsSearchDomains=[],
            extraHosts=[],
            dockerSecurityOptions=[],
            dependsOn=depends_on,
            logConfiguration=log_config,
            systemControls=[]
        )
    
    assert "image" in str(exc_info.value)