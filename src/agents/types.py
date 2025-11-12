from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class PromptTemplate(BaseModel):
    """提示词模板数据结构"""
    template_key: str = Field(description="提示词模板唯一标识符")
    version: str = Field(description="模板版本号 (例如: '1.0.0')")
    description: str = Field(description="模板描述")

    # 模板内容
    template_content: str = Field(description="Python字符串模板内容")
    required_params: list[str] = Field(description="模板所需参数列表", default_factory=list)

    # 元数据
    language: str = Field(description="模板语言", default="zh")
    notes: str = Field(description="备注信息，使用感受、优化建议等", default="")

    @classmethod
    def create_template(
        cls,
        template_key: str,
        version: str,
        description: str,
        template_content: str,
        required_params: list[str] | None = None,
        language: str = "zh",
        notes: str = ""
    ) -> "PromptTemplate":
        """
        创建提示词模板实例

        Args:
            template_key: 模板唯一标识符
            version: 版本号
            description: 模板描述
            template_content: Python字符串模板内容
            required_params: 必需参数列表
            language: 模板语言
            notes: 备注信息

        Returns:
            PromptTemplate: 提示词模板实例
        """
        return cls(
            template_key=template_key,
            version=version,
            description=description,
            template_content=template_content,
            required_params=required_params or [],
            language=language,
            notes=notes
        )

    def render(self, **kwargs) -> str:
        """
        渲染模板

        Args:
            **kwargs: 模板参数

        Returns:
            str: 渲染后的内容

        Raises:
            ValueError: 缺少必需参数
            KeyError: 参数不存在于模板中
        """
        # 检查必需参数
        missing_params = set(self.required_params) - set(kwargs.keys())
        if missing_params:
            raise ValueError(f"缺少必需参数: {', '.join(missing_params)}")

        try:
            return self.template_content.format(**kwargs)
        except KeyError as e:
            raise KeyError(f"模板中存在未定义的参数: {e}")
        except ValueError as e:
            raise ValueError(f"模板格式错误: {e}")

    def __str__(self) -> str:
        """字符串表示"""
        return f"PromptTemplate(key={self.template_key}, version={self.version})"

    def __repr__(self) -> str:
        """详细字符串表示"""
        return (f"PromptTemplate(template_key='{self.template_key}', version='{self.version}', "
                f"required_params={self.required_params}, notes='{self.notes[:50]}...')" if len(self.notes) > 50 else
                f"PromptTemplate(template_key='{self.template_key}', version='{self.version}', "
                f"required_params={self.required_params}, notes='{self.notes})")


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

