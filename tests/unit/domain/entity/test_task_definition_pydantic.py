import pytest
from pydantic import ValidationError
from ecs_taskdef.domain.entity.task_definition import (
    TaskDefinition,
    Volumes,
    VolumesHost,
    Tag,
    RuntimePlatform
)
from ecs_taskdef.domain.entity.container_definition import (
    ContainerDefinition,
    LogConfiguration,
    LogConfigurationOptions,
    PortMapping,
    DependsOn
)
from ecs_taskdef.domain.entity.environment_variable import EnvironmentVariable


def test_volumes_host_validation():
    """Test VolumesHost validation."""
    # Valid data
    host_vol = VolumesHost(sourcePath="/ecs/data")
    assert host_vol.source_path == "/ecs/data"
    
    # Serialization with aliases
    host_dict = host_vol.model_dump(by_alias=True)
    assert host_dict["sourcePath"] == "/ecs/data"


def test_volumes_validation():
    """Test Volumes validation."""
    # Volume with host path
    host_vol = VolumesHost(sourcePath="/ecs/data")
    volume = Volumes(name="host-vol", host=host_vol)
    assert volume.name == "host-vol"
    assert volume.host.source_path == "/ecs/data"
    
    # Test static generate method
    generated = Volumes.generate_host(name="data-vol", source_path="/data")
    assert generated.name == "data-vol"
    assert generated.host.source_path == "/data"
    
    # Test serialization with aliases
    vol_dict = volume.model_dump(by_alias=True)
    assert vol_dict["name"] == "host-vol"
    assert vol_dict["host"]["sourcePath"] == "/ecs/data"


def test_tag_validation():
    """Test Tag validation."""
    tag = Tag(key="Environment", value="Production")
    assert tag.key == "Environment"
    assert tag.value == "Production"
    
    # Missing required fields
    with pytest.raises(ValidationError) as exc_info:
        Tag(key="Environment")  # Missing value
    
    assert "value" in str(exc_info.value)


def test_runtime_platform_validation():
    """Test RuntimePlatform validation."""
    platform = RuntimePlatform(cpuArchitecture="X86_64")
    assert platform.cpu_architecture == "X86_64"
    
    # Invalid CPU architecture
    with pytest.raises(ValidationError) as exc_info:
        RuntimePlatform(cpuArchitecture="INVALID")
    
    assert "cpuArchitecture" in str(exc_info.value)


def test_task_definition_validation():
    """Test TaskDefinition validation with valid and invalid data."""
    # Create container definitions for task
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
    
    # Create a volume for the task
    volume = Volumes.generate_host(name="data-vol", source_path="/data")
    
    # Create tags
    tags = [Tag(key="Environment", value="Production")]
    
    # Valid task definition
    task_def = TaskDefinition(
        family="web-app",
        containerDefinitions=[container],
        volumes=[volume],
        networkMode="awsvpc",
        memory="1024",
        cpu="512",
        executionRoleArn="arn:aws:iam::123456789012:role/ecsTaskExecutionRole",
        taskRoleArn="arn:aws:iam::123456789012:role/ecsTaskRole",
        requiresCompatibilities=["FARGATE"],
        taskDefinitionArn=None,
        revision=None,
        status="ACTIVE",
        requiresAttributes=None,
        placementConstraints=[],
        compatibilities=None,
        runtimePlatform=RuntimePlatform(cpuArchitecture="X86_64"),
        enableFaultInjection=False,
        tags=tags
    )
    
    assert task_def.family == "web-app"
    assert len(task_def.container_definitions) == 1
    assert task_def.container_definitions[0].name == "web"
    assert len(task_def.volumes) == 1
    assert task_def.volumes[0].name == "data-vol"
    assert task_def.network_mode == "awsvpc"
    assert task_def.memory == "1024"
    assert task_def.cpu == "512"
    assert task_def.execution_role_arn == "arn:aws:iam::123456789012:role/ecsTaskExecutionRole"
    assert task_def.task_role_arn == "arn:aws:iam::123456789012:role/ecsTaskRole"
    assert task_def.requires_compatibilities == ["FARGATE"]
    
    # Test serialization with aliases
    task_dict = task_def.model_dump(by_alias=True)
    assert task_dict["family"] == "web-app"
    assert len(task_dict["containerDefinitions"]) == 1
    assert task_dict["networkMode"] == "awsvpc"
    assert task_dict["memory"] == "1024"
    assert task_dict["cpu"] == "512"
    assert task_dict["executionRoleArn"] == "arn:aws:iam::123456789012:role/ecsTaskExecutionRole"
    assert task_dict["taskRoleArn"] == "arn:aws:iam::123456789012:role/ecsTaskRole"
    assert task_dict["requiresCompatibilities"] == ["FARGATE"]


def test_task_definition_generate():
    """Test TaskDefinition.generate static method."""
    # Create container definitions for task
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
    
    # Create volumes for the task
    volume = Volumes.generate_host(name="data-vol", source_path="/data")
    
    # Create tags
    tags = [Tag(key="Environment", value="Production")]
    
    # Generate a task definition
    task_def = TaskDefinition.generate(
        container_definitions=[container],
        family="web-app",
        task_role_arn="arn:aws:iam::123456789012:role/ecsTaskRole",
        execution_role_arn="arn:aws:iam::123456789012:role/ecsTaskExecutionRole",
        cpu="512",
        memory="1024",
        cpu_architecture="X86_64",
        tags=tags,
        volumes=[volume],
        network_mode="awsvpc"
    )
    
    # Verify generated task definition
    assert task_def.family == "web-app"
    assert len(task_def.container_definitions) == 1
    assert task_def.container_definitions[0].name == "web"
    assert task_def.network_mode == "awsvpc"
    assert task_def.memory == "1024"
    assert task_def.cpu == "512"
    assert task_def.execution_role_arn == "arn:aws:iam::123456789012:role/ecsTaskExecutionRole"
    assert task_def.task_role_arn == "arn:aws:iam::123456789012:role/ecsTaskRole"
    assert task_def.runtime_platform.cpu_architecture == "X86_64"
    assert task_def.requires_compatibilities == ["FARGATE"]
    assert len(task_def.volumes) == 1
    assert task_def.volumes[0].name == "data-vol"


def test_task_definition_network_mode_validation():
    """Test validation of networkMode field."""
    # Valid network modes
    for mode in ["bridge", "host", "awsvpc", "none"]:
        platform = RuntimePlatform(cpuArchitecture="X86_64")
        tags = [Tag(key="Environment", value="Production")]
        
        task_def = TaskDefinition(
            family="app",
            containerDefinitions=[],
            volumes=[],
            networkMode=mode,
            taskDefinitionArn=None,
            revision=None,
            status="ACTIVE",
            requiresAttributes=None,
            placementConstraints=[],
            compatibilities=None,
            requiresCompatibilities=["FARGATE"],
            cpu="256",
            memory="512",
            taskRoleArn="arn:aws:iam::123456789012:role/role",
            executionRoleArn="arn:aws:iam::123456789012:role/role",
            runtimePlatform=platform,
            enableFaultInjection=False,
            tags=tags
        )
        assert task_def.network_mode == mode
    
    # Invalid network mode
    with pytest.raises(ValidationError) as exc_info:
        platform = RuntimePlatform(cpuArchitecture="X86_64")
        tags = [Tag(key="Environment", value="Production")]
        
        TaskDefinition(
            family="app",
            containerDefinitions=[],
            volumes=[],
            networkMode="invalid",
            taskDefinitionArn=None,
            revision=None,
            status="ACTIVE",
            requiresAttributes=None,
            placementConstraints=[],
            compatibilities=None,
            requiresCompatibilities=["FARGATE"],
            cpu="256",
            memory="512",
            taskRoleArn="arn:aws:iam::123456789012:role/role",
            executionRoleArn="arn:aws:iam::123456789012:role/role",
            runtimePlatform=platform,
            enableFaultInjection=False,
            tags=tags
        )
    
    assert "networkMode" in str(exc_info.value)


def test_task_definition_export():
    """Test the TaskDefinition export method."""
    # Create minimal task definition for export testing
    platform = RuntimePlatform(cpuArchitecture="X86_64")
    tags = [Tag(key="Environment", value="Production")]
    
    task_def = TaskDefinition(
        taskDefinitionArn="arn:aws:ecs:us-east-1:123456789012:task-definition/app:1",
        family="app",
        containerDefinitions=[],
        volumes=[],
        networkMode="awsvpc",
        revision=1,
        status="ACTIVE",
        requiresAttributes=None,
        placementConstraints=[],
        compatibilities=["FARGATE"],
        requiresCompatibilities=["FARGATE"],
        cpu="256",
        memory="512",
        taskRoleArn="arn:aws:iam::123456789012:role/role",
        executionRoleArn="arn:aws:iam::123456789012:role/role",
        runtimePlatform=platform,
        enableFaultInjection=False,
        tags=tags
    )
    
    # Export to dictionary
    export_dict = task_def.export()
    
    # Verify excluded fields are not present
    assert "taskDefinitionArn" not in export_dict
    assert "revision" not in export_dict
    assert "requiresAttributes" not in export_dict
    assert "compatibilities" not in export_dict
    
    # Verify required fields are present
    assert "family" in export_dict
    assert "networkMode" in export_dict
    assert "cpu" in export_dict
    assert "memory" in export_dict