from datetime import datetime

from ecs_taskdef.domain.entity.task_definition import (
    EphemeralStorage,
    InferenceAccelerator,
    KeyValuePair,
    ProxyConfiguration,
    RuntimePlatform,
    Tag,
    TaskDefinition,
)


def test_task_definition_extended_parameters():
    """Test that the TaskDefinition supports extended parameters."""
    # Create a minimal task definition with the new parameters
    platform = RuntimePlatform(cpuArchitecture="X86_64")
    tags = [Tag(key="Environment", value="Test")]

    # Create proxy configuration
    proxy_config = ProxyConfiguration(
        type="APPMESH",
        containerName="envoy",
        properties=[
            KeyValuePair(name="IgnoredUID", value="1337"),
            KeyValuePair(name="ProxyIngressPort", value="15000"),
            KeyValuePair(name="ProxyEgressPort", value="15001"),
        ],
    )

    # Create inference accelerator
    inference_acc = InferenceAccelerator(deviceName="device1", deviceType="eia2.medium")

    # Create ephemeral storage
    ephemeral_storage = EphemeralStorage(sizeInGiB=50)

    # Create the task definition
    task_def = TaskDefinition(
        family="test-family",
        containerDefinitions=[],
        volumes=[],
        networkMode="awsvpc",
        taskRoleArn="arn:aws:iam::123456789012:role/test-role",
        executionRoleArn="arn:aws:iam::123456789012:role/test-execution-role",
        cpu="1024",
        memory="2048",
        status="ACTIVE",
        placementConstraints=[],
        requiresCompatibilities=["FARGATE"],
        runtimePlatform=platform,
        enableFaultInjection=False,
        tags=tags,
        ipcMode="task",
        pidMode="task",
        proxyConfiguration=proxy_config,
        inferenceAccelerators=[inference_acc],
        ephemeralStorage=ephemeral_storage,
        registeredAt=datetime.now(),
        registeredBy="test-user",
        deregisteredAt=None,
    )

    # Verify fields are correctly set
    assert task_def.ipc_mode == "task"
    assert task_def.pid_mode == "task"
    assert isinstance(task_def.proxy_configuration, ProxyConfiguration)
    assert task_def.proxy_configuration.container_name == "envoy"
    assert len(task_def.inference_accelerators) == 1
    assert task_def.inference_accelerators[0].device_name == "device1"
    assert task_def.ephemeral_storage.size_in_gi_b == 50
    assert isinstance(task_def.registered_at, datetime)
    assert task_def.registered_by == "test-user"
    assert task_def.deregistered_at is None


def test_export_excludes_registration_metadata():
    """Test that export method correctly excludes registration metadata."""
    platform = RuntimePlatform(cpuArchitecture="X86_64")
    tags = [Tag(key="Environment", value="Test")]

    task_def = TaskDefinition(
        family="test-family",
        containerDefinitions=[],
        volumes=[],
        networkMode="awsvpc",
        taskRoleArn="arn:aws:iam::123456789012:role/test-role",
        executionRoleArn="arn:aws:iam::123456789012:role/test-execution-role",
        cpu="1024",
        memory="2048",
        status="ACTIVE",
        placementConstraints=[],
        requiresCompatibilities=["FARGATE"],
        runtimePlatform=platform,
        enableFaultInjection=False,
        tags=tags,
        registeredAt=datetime.now(),
        registeredBy="test-user",
        deregisteredAt=None,
    )

    exported = task_def.export()

    # Verify registration metadata is excluded
    assert "registeredAt" not in exported
    assert "registeredBy" not in exported
    assert "deregisteredAt" not in exported


def test_task_definition_generate_with_extended_parameters():
    """Test that TaskDefinition.generate can include extended parameters."""
    tags = [Tag(key="Environment", value="Test")]

    # Create proxy configuration
    proxy_config = ProxyConfiguration(
        type="APPMESH", containerName="envoy", properties=[KeyValuePair(name="ProxyIngressPort", value="15000")]
    )

    # Create inference accelerator
    inference_acc = InferenceAccelerator(deviceName="device1", deviceType="eia2.medium")

    # Create ephemeral storage
    ephemeral_storage = EphemeralStorage(sizeInGiB=50)

    # Generate the task definition with extended parameters
    task_def = TaskDefinition.generate(
        container_definitions=[],
        family="test-family",
        task_role_arn="arn:aws:iam::123456789012:role/test-role",
        execution_role_arn="arn:aws:iam::123456789012:role/test-execution-role",
        cpu="1024",
        memory="2048",
        cpu_architecture="X86_64",
        tags=tags,
        ipc_mode="task",
        pid_mode="task",
        proxy_configuration=proxy_config,
        inference_accelerators=[inference_acc],
        ephemeral_storage=ephemeral_storage,
    )

    # Verify the new fields are correctly set
    assert task_def.ipc_mode == "task"
    assert task_def.pid_mode == "task"
    assert task_def.proxy_configuration.container_name == "envoy"
    assert len(task_def.inference_accelerators) == 1
    assert task_def.inference_accelerators[0].device_type == "eia2.medium"
    assert task_def.ephemeral_storage.size_in_gi_b == 50
