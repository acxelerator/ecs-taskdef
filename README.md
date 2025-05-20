# ecs-taskdef

# install

```shell
$ rye add ecs-taskdef --git=https://github.com/acxelerator/ecs-taskdef
```

# usage

to generate taskdef run the example code below.

```python
from ecs_taskdef import EnvironmentVariable
from ecs_taskdef.domain.entity.task_definition import (
    TaskDefinition,
    Tag,
)
from ecs_taskdef.domain.entity.container_definition import (
    ContainerDefinition,
    PortMapping,
    LogConfiguration,
)
from ecs_taskdef.domain.service import SecretValue
import json


def _gen_taskdef(secrets: dict) -> dict:
    container_def = ContainerDefinition.generate(
        name="container-name",
        image="000011112222.dkr.ecr.ap-northeast-1.amazonaws.com/name:tag",
        cpu=0,
        memory_reservation=2000,
        environment=EnvironmentVariable.from_dict(secrets),
        port_mappings=[
            PortMapping(containerPort=80, hostPort=80, protocol="tcp"),
        ],
        log_configuration=LogConfiguration.generate(group_name="/aws/ecs/container", stream_prefix="name"),
    )

    taskdef = TaskDefinition.generate(
        container_definitions=[container_def],
        family="family-name",
        task_role_arn="arn:aws:iam::000011112222:role/ecs-task-stg",
        execution_role_arn="arn:aws:iam::000011112222:role/ecs-execution-stg",
        cpu="1024",
        memory="2048",
        cpu_architecture="ARM64",
        tags=[],
    ).export()
    taskdef.pop("tags")
    return taskdef


def main():
    secrets = SecretValue().get_from_secrets_manager(
        secret_name=f"environment-variables"
    )
    taskdef = _gen_taskdef(secrets=secrets)

    with open("taskdef.json", "w") as f:
        json.dump(taskdef, f, indent=2)


if __name__ == "__main__":
    main()
```

# Development

## Testing

The project uses pytest for testing. Run the tests locally with:

```shell
python -m pytest
```

For test coverage information:

```shell
python -m pytest --cov=ecs_taskdef
```

Tests are automatically run on GitHub Actions for all push and pull request events on the main branch.

