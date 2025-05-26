from pydantic import BaseModel, Field


class EnvironmentVariable(BaseModel):
    name: str = Field()
    value: str = Field()

    @staticmethod
    def from_dict(d: dict) -> list["EnvironmentVariable"]:
        result = []
        for k, v in d.items():
            result.append(EnvironmentVariable(name=k, value=v))
        return result
