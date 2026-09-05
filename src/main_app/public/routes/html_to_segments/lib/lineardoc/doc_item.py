""" """

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

from .text_block import TextBlock

ITEM_TYPES = Literal["open", "close", "blockspace", "textblock"]
ITEM_OBJECT_TYPES = dict[str, Any] | TextBlock | str


@dataclass
class DocItem:
    item_type: ITEM_TYPES
    item: ITEM_OBJECT_TYPES | Any
    item_text_block: TextBlock | None = None
    item_str: str | None = None
    item_dict: dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> dict[str, Any]:
        return {"type": self.item_type, "item": self.item}

    def __getitem__(self, key: str) -> Any:
        # connect keys to object properties
        if key == "type":
            return self.item_type
        elif key == "item":
            return self.item
        else:
            raise KeyError(f"key '{key}' not found in Item")

    @classmethod
    def from_any(cls, item_type: ITEM_TYPES, obj: ITEM_OBJECT_TYPES | Any) -> DocItem:
        result = cls(item_type=item_type, item=obj)
        if isinstance(obj, TextBlock):
            result.item_text_block = obj

        elif isinstance(obj, dict):
            result.item_dict = obj

        elif isinstance(obj, str):
            result.item_str = obj
        else:
            raise TypeError(f"Invalid type for Item: {type(obj)}")

        return result


__all__ = [
    "DocItem",
]
