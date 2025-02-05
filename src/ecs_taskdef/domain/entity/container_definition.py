from pydantic import BaseModel, Field
from .environment_variable import EnvironmentVariable
from typing import Literal, Optional

ULIMIT_NAME = Literal[
    "core",
    "cpu",
    "data",
    "fsize",
    "locks",
    "memlock",
    "msgqueue",
    "nice",
    "nofile",
    "nproc",
    "rss",
    "rtprio",
    "rttime",
    "sigpending",
    "stack",
]
PROTOCOL = Literal["tcp", "udp"]


class ULimit(BaseModel):
    name: str
    soft_limit: int = Field(alias="softLimit")
    hard_limit: int = Field(alias="hardLimit")


class PortMapping(BaseModel):
    container_port: int = Field(alias="containerPort")
    host_port: int = Field(alias="hostPort")
    protocol: Optional[PROTOCOL]


class MountPoint(BaseModel):
    source_volume: str = Field(alias="sourceVolume")
    container_path: str = Field(alias="containerPath")
    read_only: bool | None = Field(alias="readOnly")


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


class Secrets(BaseModel):
    name: str = Field(description="environment variable name")
    value_from: str = Field(alias="valueFrom")


class ContainerDefinition(BaseModel):
    name: str = Field(alias="name")
    image: str = Field(alias="image")
    cpu: int = Field(alias="cpu")
    memory_reservation: int = Field(alias="memoryReservation")
    links: Optional[list] = Field(alias="links", default_factory=list)
    port_mappings: list = Field(alias="portMappings")
    essential: Optional[bool] = Field(alias="essential")
    entry_point: Optional[list[str]] = Field(alias="entryPoint", default_factory=list)
    command: Optional[list[str]] = Field(alias="command", default_factory=list)
    environment: Optional[list[EnvironmentVariable]] = Field(
        alias="environment", default_factory=list
    )
    environment_files: list = Field(alias="environmentFiles")
    mount_points: Optional[list] = Field(alias="mountPoints", default_factory=list)
    volumes_from: Optional[list] = Field(alias="volumesFrom", default_factory=list)
    secrets: Optional[list[Secrets]] = Field(alias="secrets", default_factory=list)
    dns_servers: list = Field(alias="dnsServers")
    dns_search_domains: list = Field(alias="dnsSearchDomains")
    extra_hosts: list = Field(alias="extraHosts")
    docker_security_options: list = Field(alias="dockerSecurityOptions")
    docker_labels: Optional[dict[str, str]] = Field(
        alias="dockerLabels", default_factory=dict
    )
    u_limits: Optional[list[ULimit]] = Field(alias="ulimits", default_factory=list)
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
        log_configuration: LogConfiguration,
        essential: bool = True,
        mount_points: list[MountPoint] | None = None,
        u_limits: list[ULimit] | None = None,
    ) -> "ContainerDefinition":
        _mount_points = mount_points
        if _mount_points is None:
            _mount_points = []
        _u_limits = u_limits
        if _u_limits is None:
            _u_limits = []
        return ContainerDefinition(
            name=name,
            image=image,
            cpu=cpu,
            memoryReservation=memory_reservation,
            portMappings=port_mappings,
            essential=essential,
            environment=environment,
            environmentFiles=[],
            mountPoints=_mount_points,
            dnsServers=[],
            dnsSearchDomains=[],
            extraHosts=[],
            dockerSecurityOptions=[],
            ulimits=_u_limits,
            logConfiguration=log_configuration,
            systemControls=[],
        )
