from pydantic import BaseModel, Field
from .environment_variable import EnvironmentVariable


class ULimit(BaseModel):
    name: str
    soft_limit: int = Field(alias="softLimit")
    hard_limit: int = Field(alias="hardLimit")


class LogConfigurationOptions(BaseModel):
    awslogs_group: str = Field(alias="awslogs-group")
    awslogs_region: str = Field(alias="awslogs-region")
    awslogs_stream_prefix: str = Field(alias="awslogs-stream-prefix")


class LogConfiguration(BaseModel):
    log_driver: str = Field(alias="logDriver")
    options: LogConfigurationOptions = Field(alias="options")
    secret_options: list = Field(alias="secretOptions")


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


class TaskDefinition(BaseModel):
    task_definition_arn: str = Field(alias="taskDefinitionArn")
    container_definitions: list[ContainerDefinition] = Field(
        alias="containerDefinitions"
    )
    family: str = Field(alias="family")
    task_role_arn: str = Field(alias="taskRoleArn")
    execution_role_arn: str = Field(alias="executionRoleArn")
    network_mode: str = Field(alias="networkMode")
    revision: int = Field(alias="revision")
    volumes: list = Field(alias="volumes")
    status: str = Field(alias="status")
    requires_attributes: list = Field(alias="requiresAttributes")
    placement_constraints: list = Field(alias="placementConstraints")
    compatibilities: list[str] = Field(alias="compatibilities")
    requires_compatibilities: list[str] = Field(alias="requiresCompatibilities")
    cpu: str = Field(alias="cpu")
    memory: str = Field(alias="memory")

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
