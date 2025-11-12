from pydantic import BaseModel, Field


class ErExtractEntity(BaseModel):
    """实体提取结果中的实体"""
    name: str = Field(description="实体名称")
    category: str = Field(description="实体类别")
    desc: str = Field(description="实体描述")


class ErExtractRelation(BaseModel):
    """实体提取结果中的关系"""
    source: str = Field(description="关系源实体名称")
    target: str = Field(description="关系目标实体名称")
    desc: str = Field(description="关系描述")


class ErExtractResult(BaseModel):
    """实体关系提取结果"""
    entities: list[ErExtractEntity] = Field(description="实体列表")
    relationships: list[ErExtractRelation] = Field(description="关系列表")

