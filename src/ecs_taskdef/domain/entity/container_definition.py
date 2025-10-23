from typing import Dict, Literal, Optional

from pydantic import BaseModel, Field

from .environment_variable import EnvironmentVariable

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


class DependsOn(BaseModel):
    condition: Literal["START", "COMPLETE", "SUCCESS", "HEALTHY"]
    container_name: str = Field(alias="containerName")


class VolumesFrom(BaseModel):
    read_only: bool = Field(alias="readOnly")
    source_container: str = Field(alias="sourceContainer")


class LogConfiguration(BaseModel):
    log_driver: str = Field(alias="logDriver")
    options: LogConfigurationOptions = Field(alias="options")
    secret_options: list = Field(alias="secretOptions")

    @staticmethod
    def generate(group_name: str, stream_prefix: str, region: str = "ap-northeast-1") -> "LogConfiguration":
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


class HealthCheck(BaseModel):
    command: list[str]
    interval: int
    timeout: int
    retries: int
    start_period: Optional[int] = Field(alias="startPeriod")


class RepositoryCredentials(BaseModel):
    credentials_parameter: str = Field(alias="credentialsParameter")


class ResourceRequirement(BaseModel):
    type: Literal["GPU", "InferenceAccelerator"]
    value: str


class FirelensConfiguration(BaseModel):
    type: Literal["fluentd", "fluentbit"]
    options: Optional[Dict[str, str]] = Field(default_factory=dict)


class SystemControl(BaseModel):
    namespace: str
    value: str


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
    environment: Optional[list[EnvironmentVariable]] = Field(alias="environment", default_factory=list)
    environment_files: list = Field(alias="environmentFiles")
    mount_points: Optional[list] = Field(alias="mountPoints", default_factory=list)
    volumes_from: Optional[list] = Field(alias="volumesFrom", default_factory=list)
    secrets: Optional[list[Secrets]] = Field(alias="secrets", default_factory=list)
    dns_servers: list = Field(alias="dnsServers")
    dns_search_domains: list = Field(alias="dnsSearchDomains")
    extra_hosts: list = Field(alias="extraHosts")
    docker_security_options: list = Field(alias="dockerSecurityOptions")
    docker_labels: Optional[dict[str, str]] = Field(alias="dockerLabels", default_factory=dict)
    depends_on: Optional[list[DependsOn]] = Field(alias="dependsOn")
    u_limits: Optional[list[ULimit]] = Field(alias="ulimits", default_factory=list)
    log_configuration: LogConfiguration = Field(alias="logConfiguration")
    system_controls: list = Field(alias="systemControls")
    health_check: Optional[HealthCheck] = Field(alias="healthCheck", default=None)
    repository_credentials: Optional[RepositoryCredentials] = Field(alias="repositoryCredentials", default=None)
    resource_requirements: Optional[list[ResourceRequirement]] = Field(
        alias="resourceRequirements", default_factory=list
    )
    firelens_configuration: Optional[FirelensConfiguration] = Field(alias="firelensConfiguration", default=None)
    start_timeout: Optional[int] = Field(alias="startTimeout", default=None)
    stop_timeout: Optional[int] = Field(alias="stopTimeout", default=None)
    privileged: Optional[bool] = Field(default=None)
    readonly_root_filesystem: Optional[bool] = Field(alias="readonlyRootFilesystem", default=None)

    @staticmethod
    def generate(
        name: str,
        image: str,
        cpu: int,
        memory_reservation: int,
        port_mappings: list[PortMapping],
        log_configuration: LogConfiguration,
        essential: bool = True,
        environment: list[EnvironmentVariable] | None = None,
        secrets: list[Secrets] | None = None,
        depends_on: list[DependsOn] | None = None,
        volumes_from: list[VolumesFrom] | None = None,
        mount_points: list[MountPoint] | None = None,
        u_limits: list[ULimit] | None = None,
        health_check: HealthCheck | None = None,
        repository_credentials: RepositoryCredentials | None = None,
        resource_requirements: list[ResourceRequirement] | None = None,
        firelens_configuration: FirelensConfiguration | None = None,
        start_timeout: int | None = None,
        stop_timeout: int | None = None,
        privileged: bool | None = None,
        readonly_root_filesystem: bool | None = None,
    ) -> "ContainerDefinition":
        _mount_points = mount_points
        if _mount_points is None:
            _mount_points = []
        _u_limits = u_limits
        if _u_limits is None:
            _u_limits = []
        _depends_on = depends_on
        if _depends_on is None:
            _depends_on = []
        _volumes_from = volumes_from
        if _volumes_from is None:
            _volumes_from = []
        _resource_requirements = resource_requirements
        if _resource_requirements is None:
            _resource_requirements = []
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
            volumesFrom=_volumes_from,
            dnsServers=[],
            dnsSearchDomains=[],
            extraHosts=[],
            dockerSecurityOptions=[],
            dependsOn=_depends_on,
            ulimits=_u_limits,
            logConfiguration=log_configuration,
            systemControls=[],
            healthCheck=health_check,
            repositoryCredentials=repository_credentials,
            resourceRequirements=_resource_requirements,
            firelensConfiguration=firelens_configuration,
            startTimeout=start_timeout,
            stopTimeout=stop_timeout,
            privileged=privileged,
            readonlyRootFilesystem=readonly_root_filesystem,
            # entryPoint=[],
            # command=[],
            # links=[],
            secrets=secrets,
            # dockerLabels={},
        )
