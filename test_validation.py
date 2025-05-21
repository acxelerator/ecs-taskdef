#!/usr/bin/env python
from pydantic import ValidationError

from ecs_taskdef.domain.entity.task_definition import RuntimePlatform, Tag, TaskDefinition


def test_valid_combinations():
    platform = RuntimePlatform(cpuArchitecture="X86_64")
    tags = [Tag(key="Environment", value="Production")]

    # Test valid combinations
    valid_combinations = [
        ("256", "512"),  # 0.25 vCPU - 512MB
        ("512", "1024"),  # 0.5 vCPU - 1GB
        ("1024", "2048"),  # 1 vCPU - 2GB
        ("2048", "4096"),  # 2 vCPU - 4GB
        ("4096", "8192"),  # 4 vCPU - 8GB
        ("8192", "16384"),  # 8 vCPU - 16GB
        ("16384", "32768"),  # 16 vCPU - 32GB
    ]

    print("Testing valid combinations...")
    for i, (cpu, memory) in enumerate(valid_combinations):
        try:
            task_def = TaskDefinition(
                family="app",
                containerDefinitions=[],
                volumes=[],
                networkMode="awsvpc",
                taskDefinitionArn=None,
                revision=None,
                status="ACTIVE",
                requiresAttributes=None,
                placementConstraints=[],
                compatibilities=None,
                requiresCompatibilities=["FARGATE"],
                cpu=cpu,
                memory=memory,
                taskRoleArn="arn:aws:iam::123456789012:role/role",
                executionRoleArn="arn:aws:iam::123456789012:role/role",
                runtimePlatform=platform,
                enableFaultInjection=False,
                tags=tags,
            )
            print(f"✅ Valid combination {i + 1}: CPU={cpu}, Memory={memory}")
        except ValidationError as e:
            print(f"❌ Failed for valid combination: CPU={cpu}, Memory={memory}")
            print(f"Error: {e}")


def test_invalid_combinations():
    platform = RuntimePlatform(cpuArchitecture="X86_64")
    tags = [Tag(key="Environment", value="Production")]

    # Test invalid combinations
    invalid_combinations = [
        ("256", "8192"),  # 0.25 vCPU with 8GB (too much memory)
        ("512", "16384"),  # 0.5 vCPU with 16GB (too much memory)
        ("1024", "30720"),  # 1 vCPU with 30GB (too much memory)
        ("2048", "32768"),  # 2 vCPU with 32GB (too much memory)
        ("4096", "61440"),  # 4 vCPU with 60GB (too much memory)
    ]

    print("\nTesting invalid combinations...")
    for i, (cpu, memory) in enumerate(invalid_combinations):
        try:
            task_def = TaskDefinition(
                family="app",
                containerDefinitions=[],
                volumes=[],
                networkMode="awsvpc",
                taskDefinitionArn=None,
                revision=None,
                status="ACTIVE",
                requiresAttributes=None,
                placementConstraints=[],
                compatibilities=None,
                requiresCompatibilities=["FARGATE"],
                cpu=cpu,
                memory=memory,
                taskRoleArn="arn:aws:iam::123456789012:role/role",
                executionRoleArn="arn:aws:iam::123456789012:role/role",
                runtimePlatform=platform,
                enableFaultInjection=False,
                tags=tags,
            )
            print(f"❌ Invalid combination {i + 1} was accepted: CPU={cpu}, Memory={memory}")
        except ValidationError as e:
            print(f"✅ Correctly rejected invalid combination {i + 1}: CPU={cpu}, Memory={memory}")
            print(f"  Error: {e}")


if __name__ == "__main__":
    test_valid_combinations()
    test_invalid_combinations()
