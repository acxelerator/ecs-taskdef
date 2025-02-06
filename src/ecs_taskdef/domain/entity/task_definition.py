from pydantic import BaseModel, Field
from .container_definition import ContainerDefinition
from .environment_variable import EnvironmentVariable
from typing import Literal, Optional

NETWORK_MODE = Literal["none", "bridge", "awsvpc", "host"]
CPU_ARCHITECTURE = Literal["X86_64", "ARM64"]


class RuntimePlatform(BaseModel):
    cpu_architecture: CPU_ARCHITECTURE = Field(alias="cpuArchitecture")


class Tag(BaseModel):
    key: str
    value: str


class VolumesHost(BaseModel):
    source_path: str = Field(alias="sourcePath")


class Volumes(BaseModel):
    name: str
    host: VolumesHost

    @staticmethod
    def generate_host(name: str, source_path: str):
        return Volumes(name=name, host=VolumesHost(sourcePath=source_path))


class TaskDefinition(BaseModel):
    task_definition_arn: Optional[str] = Field(alias="taskDefinitionArn")
    container_definitions: list[ContainerDefinition] = Field(
        alias="containerDefinitions"
    )
    family: str = Field(alias="family")
    task_role_arn: str = Field(alias="taskRoleArn")
    execution_role_arn: str = Field(alias="executionRoleArn")
    network_mode: NETWORK_MODE = Field(alias="networkMode")
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
        cpu_architecture: CPU_ARCHITECTURE,
        tags: list[Tag],
        volumes: list[Volumes] | None = None,
        network_mode: NETWORK_MODE = "awsvpc",
    ) -> "TaskDefinition":
        _volumes = volumes
        if _volumes is None:
            _volumes = []
        return TaskDefinition(
            taskDefinitionArn=None,
            containerDefinitions=container_definitions,
            family=family,
            taskRoleArn=task_role_arn,
            executionRoleArn=execution_role_arn,
            networkMode=network_mode,
            revision=None,
            volumes=_volumes,
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
