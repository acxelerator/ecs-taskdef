from pydantic import BaseModel, Field
from .environment_variable import EnvironmentVariable
from typing import Literal, Optional


class ULimit(BaseModel):
    name: str
    soft_limit: int = Field(alias="softLimit")
    hard_limit: int = Field(alias="hardLimit")


class PortMapping(BaseModel):
    container_port: int = Field(alias="containerPort")
    host_port: int = Field(alias="hostPort")
    protocol: str


class LogConfigurationOptions(BaseModel):
    awslogs_group: str = Field(alias="awslogs-group")
    awslogs_region: str = Field(alias="awslogs-region")
    awslogs_stream_prefix: str = Field(alias="awslogs-stream-prefix")


class LogConfiguration(BaseModel):
    log_driver: str = Field(alias="logDriver")
    options: LogConfigurationOptions = Field(alias="options")
    secret_options: list = Field(alias="secretOptions")

    @staticmethod
    def generate(
        group_name: str, stream_prefix: str, region: str = "ap-northeast-1"
    ) -> "LogConfiguration":
        options = LogConfigurationOptions(
            **{
                "awslogs-group": group_name,
                "awslogs-region": region,
                "awslogs-stream-prefix": stream_prefix,
            }
        )
        return LogConfiguration(
            logDriver="awslogs",
            options=options,
            secretOptions=[],
        )


class ContainerDefinition(BaseModel):
    name: str = Field(alias="name")
    image: str = Field(alias="image")
    cpu: int = Field(alias="cpu")
    memory_reservation: int = Field(alias="memoryReservation")
    links: list = Field(alias="links")
    port_mappings: list = Field(alias="portMappings")
    essential: bool = Field(alias="essential")
    entry_point: list = Field(alias="entryPoint")
    command: list[str] = Field(alias="command")
    environment: list[EnvironmentVariable] = Field(alias="environment")
    environment_files: list = Field(alias="environmentFiles")
    mount_points: list = Field(alias="mountPoints")
    volumes_from: list = Field(alias="volumesFrom")
    secrets: list = Field(alias="secrets")
    dns_servers: list = Field(alias="dnsServers")
    dns_search_domains: list = Field(alias="dnsSearchDomains")
    extra_hosts: list = Field(alias="extraHosts")
    docker_security_options: list = Field(alias="dockerSecurityOptions")
    docker_labels: dict = Field(alias="dockerLabels")
    u_limits: list[ULimit] = Field(alias="ulimits")
    log_configuration: LogConfiguration = Field(alias="logConfiguration")
    system_controls: list = Field(alias="systemControls")

    @staticmethod
    def generate(
        name: str,
        image: str,
        cpu: int,
        memory_reservation: int,
        environment: list[EnvironmentVariable],
        port_mappings: list[PortMapping],
        essential: bool,
        log_configuration: LogConfiguration,
    ) -> "ContainerDefinition":
        return ContainerDefinition(
            name=name,
            image=image,
            cpu=cpu,
            memoryReservation=memory_reservation,
            links=[],
            portMappings=port_mappings,
            essential=essential,
            entryPoint=[],
            command=[],
            environment=environment,
            environmentFiles=[],
            mountPoints=[],
            volumesFrom=[],
            secrets=[],
            dnsServers=[],
            dnsSearchDomains=[],
            extraHosts=[],
            dockerSecurityOptions=[],
            dockerLabels={},
            ulimits=[],
            logConfiguration=log_configuration,
            systemControls=[],
        )


class RuntimePlatform(BaseModel):
    cpu_architecture: str = Field(alias="cpuArchitecture")


class Tag(BaseModel):
    key: str
    value: str


class TaskDefinition(BaseModel):
    task_definition_arn: Optional[str] = Field(alias="taskDefinitionArn")
    container_definitions: list[ContainerDefinition] = Field(
        alias="containerDefinitions"
    )
    family: str = Field(alias="family")
    task_role_arn: str = Field(alias="taskRoleArn")
    execution_role_arn: str = Field(alias="executionRoleArn")
    network_mode: str = Field(alias="networkMode")
    revision: Optional[int] = Field(alias="revision")
    volumes: list = Field(alias="volumes")
    status: Literal["ACTIVE", "INACTIVE"] = Field(alias="status")
    requires_attributes: Optional[list] = Field(alias="requiresAttributes")
    placement_constraints: list = Field(alias="placementConstraints")
    compatibilities: Optional[list[str]] = Field(alias="compatibilities")
    requires_compatibilities: list[str] = Field(alias="requiresCompatibilities")
    cpu: str = Field(alias="cpu")
    memory: str = Field(alias="memory")
    runtime_platform: RuntimePlatform = Field(alias="runtimePlatform")
    enable_fault_injection: bool = Field(alias="enableFaultInjection")
    tags: list[Tag]

    @staticmethod
    def generate(
        container_definitions: list[ContainerDefinition],
        family: str,
        task_role_arn: str,
        execution_role_arn: str,
        cpu: str,
        memory: str,
        cpu_architecture: str,
        tags: list[Tag],
    ) -> "TaskDefinition":
        return TaskDefinition(
            taskDefinitionArn=None,
            containerDefinitions=container_definitions,
            family=family,
            taskRoleArn=task_role_arn,
            executionRoleArn=execution_role_arn,
            networkMode="awsvpc",
            revision=None,
            volumes=[],
            status="ACTIVE",
            requiresAttributes=None,
            compatibilities=[],
            placementConstraints=[],
            requiresCompatibilities=["FARGATE"],
            cpu=cpu,
            memory=memory,
            runtimePlatform=RuntimePlatform(cpuArchitecture=cpu_architecture),
            enableFaultInjection=False,
            tags=tags,
        )

    def get_container_definition_by_name(self, name: str) -> ContainerDefinition | None:
        for c in self.container_definitions:
            if c.name == name:
                return c
        return None

    def update_container_definition_by_name(
        self, name: str, container_definition: ContainerDefinition
    ) -> "TaskDefinition":
        self.container_definitions = [
            c for c in self.container_definitions if c.name != name
        ]
        self.container_definitions.append(container_definition)
        return self

    def __repr__(self) -> str:
        return f"""
        cpu: {self.cpu}
        memory: {self.memory}
        cpu_architecture: {self.runtime_platform.cpu_architecture}
        """

    def export(self) -> dict:
        return self.model_dump(
            by_alias=True,
            exclude={
                "task_definition_arn",
                "requires_attributes",
                "compatibilities",
                "revision",
            },
        )
