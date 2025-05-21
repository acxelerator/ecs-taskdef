from ecs_taskdef.domain.entity.container_definition import (
    ContainerDefinition,
    EnvironmentVariable,
    FirelensConfiguration,
    HealthCheck,
    LogConfiguration,
    PortMapping,
    RepositoryCredentials,
    ResourceRequirement,
)


def test_container_definition_extended_parameters():
    """Test that ContainerDefinition supports extended parameters."""
    # Create required components
    log_config = LogConfiguration(
        logDriver="awslogs",
        options={"awslogs-group": "test-group", "awslogs-region": "us-west-2", "awslogs-stream-prefix": "test"},
        secretOptions=[],
    )

    # Create health check
    health_check = HealthCheck(
        command=["CMD-SHELL", "curl -f http://localhost/ || exit 1"], interval=30, timeout=5, retries=3, startPeriod=60
    )

    # Create repository credentials
    repo_creds = RepositoryCredentials(
        credentialsParameter="arn:aws:secretsmanager:region:aws_account_id:secret:my-secret"
    )

    # Create resource requirement
    resource_req = ResourceRequirement(type="GPU", value="1")

    # Create firelens configuration
    firelens_config = FirelensConfiguration(type="fluentbit", options={"enable-ecs-log-metadata": "true"})

    # Create the container definition
    container_def = ContainerDefinition(
        name="test-container",
        image="test-image:latest",
        cpu=256,
        memoryReservation=512,
        portMappings=[],
        essential=True,
        environment=[],
        environmentFiles=[],
        mountPoints=[],
        volumesFrom=[],
        dnsServers=[],
        dnsSearchDomains=[],
        extraHosts=[],
        dockerSecurityOptions=[],
        logConfiguration=log_config,
        systemControls=[],
        healthCheck=health_check,
        repositoryCredentials=repo_creds,
        resourceRequirements=[resource_req],
        firelensConfiguration=firelens_config,
        startTimeout=120,
        stopTimeout=30,
        privileged=True,
        readonlyRootFilesystem=False,
    )

    # Verify fields are correctly set
    assert container_def.health_check.command == ["CMD-SHELL", "curl -f http://localhost/ || exit 1"]
    assert container_def.health_check.interval == 30
    assert container_def.health_check.timeout == 5
    assert container_def.health_check.retries == 3
    credentials_param = "arn:aws:secretsmanager:region:aws_account_id:secret:my-secret"
    assert container_def.repository_credentials.credentials_parameter == credentials_param
    assert len(container_def.resource_requirements) == 1
    assert container_def.resource_requirements[0].type == "GPU"
    assert container_def.resource_requirements[0].value == "1"

    assert container_def.firelens_configuration.type == "fluentbit"
    assert container_def.firelens_configuration.options["enable-ecs-log-metadata"] == "true"

    assert container_def.start_timeout == 120
    assert container_def.stop_timeout == 30
    assert container_def.privileged is True
    assert container_def.readonly_root_filesystem is False


def test_container_definition_generate_with_extended_parameters():
    """Test that ContainerDefinition.generate can include extended parameters."""
    # Create required components
    env_vars = [EnvironmentVariable(name="ENV_VAR", value="value")]
    port_mappings = [PortMapping(containerPort=80, hostPort=80, protocol="tcp")]
    log_config = LogConfiguration.generate(group_name="test-group", stream_prefix="test", region="us-west-2")

    # Create health check
    health_check = HealthCheck(
        command=["CMD-SHELL", "curl -f http://localhost/ || exit 1"], interval=30, timeout=5, retries=3, startPeriod=60
    )

    # Create repository credentials
    repo_creds = RepositoryCredentials(
        credentialsParameter="arn:aws:secretsmanager:region:aws_account_id:secret:my-secret"
    )

    # Create resource requirement
    resource_req = ResourceRequirement(type="GPU", value="1")

    # Create firelens configuration
    firelens_config = FirelensConfiguration(type="fluentbit", options={"enable-ecs-log-metadata": "true"})

    # Generate the container definition with extended parameters
    container_def = ContainerDefinition.generate(
        name="test-container",
        image="test-image:latest",
        cpu=256,
        memory_reservation=512,
        environment=env_vars,
        port_mappings=port_mappings,
        log_configuration=log_config,
        health_check=health_check,
        repository_credentials=repo_creds,
        resource_requirements=[resource_req],
        firelens_configuration=firelens_config,
        start_timeout=120,
        stop_timeout=30,
        privileged=True,
        readonly_root_filesystem=False,
    )

    # Verify the new fields are correctly set
    credentials_param = "arn:aws:secretsmanager:region:aws_account_id:secret:my-secret"
    assert container_def.health_check.command == ["CMD-SHELL", "curl -f http://localhost/ || exit 1"]
    assert container_def.health_check.interval == 30
    assert container_def.repository_credentials.credentials_parameter == credentials_param
    assert container_def.stop_timeout == 30
    assert container_def.privileged is True
    assert container_def.readonly_root_filesystem is False
