from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator

from .container_definition import ContainerDefinition

NETWORK_MODE = Literal["none", "bridge", "awsvpc", "host"]
CPU_ARCHITECTURE = Literal["X86_64", "ARM64"]

# Valid CPU and memory combinations for Fargate tasks
# Based on AWS documentation
CPU_MEMORY_COMBINATIONS = {
    "256": ["512", "1024", "2048"],  # 0.25 vCPU
    "512": ["1024", "2048", "3072", "4096"],  # 0.5 vCPU
    "1024": ["2048", "3072", "4096", "5120", "6144", "7168", "8192"],  # 1 vCPU
    "2048": [  # 2 vCPU
        "4096",
        "5120",
        "6144",
        "7168",
        "8192",
        "9216",
        "10240",
        "11264",
        "12288",
        "13312",
        "14336",
        "15360",
        "16384",
    ],
    "4096": [  # 4 vCPU
        "8192",
        "9216",
        "10240",
        "11264",
        "12288",
        "13312",
        "14336",
        "15360",
        "16384",
        "17408",
        "18432",
        "19456",
        "20480",
        "21504",
        "22528",
        "23552",
        "24576",
        "25600",
        "26624",
        "27648",
        "28672",
        "29696",
        "30720",
    ],
}

# Extend the list for 8 vCPU (16GB-60GB in 1GB increments)
CPU_MEMORY_COMBINATIONS["8192"] = [str(i * 1024) for i in range(16, 61)]

# Extend the list for 16 vCPU (32GB-120GB in 1GB increments)
CPU_MEMORY_COMBINATIONS["16384"] = [str(i * 1024) for i in range(32, 121)]


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
    container_definitions: list[ContainerDefinition] = Field(alias="containerDefinitions")
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

    # Validator for CPU and memory combinations
    @field_validator("memory")
    def validate_cpu_memory_combination(cls, memory_value, info):
        cpu_value = info.data.get("cpu")
        # Skip validation if CPU is not provided
        if not cpu_value:
            return memory_value

        # Check if CPU is in the valid CPU list
        if cpu_value not in CPU_MEMORY_COMBINATIONS:
            valid_cpus = list(CPU_MEMORY_COMBINATIONS.keys())
            raise ValueError(f"Invalid CPU value: {cpu_value}. Must be one of {valid_cpus}")

        # Check if memory is a valid combination with the CPU
        valid_memories = CPU_MEMORY_COMBINATIONS[cpu_value]
        if memory_value not in valid_memories:
            raise ValueError(
                f"Invalid CPU and memory combination. For CPU {cpu_value}, valid memory values are: {valid_memories}"
            )

        return memory_value

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
        self.container_definitions = [c for c in self.container_definitions if c.name != name]
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
