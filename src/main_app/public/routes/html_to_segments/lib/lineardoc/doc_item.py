""" """

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

from .text_block import TextBlock

ITEM_TYPES_STR = Literal["open", "close"]


@dataclass
class ItemBase:
    item: Any
    item_type: Any

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


@dataclass
class DocTextBlock(ItemBase):
    item: TextBlock
    item_type: str = "textblock"

    @classmethod
    def from_any(cls, item_type: str, obj: TextBlock):
        return cls(item_type=item_type, item=obj)


@dataclass
class DocDict(ItemBase):
    item_type: ITEM_TYPES_STR
    item: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_any(cls, item_type: ITEM_TYPES_STR, obj: dict[str, Any]):
        return cls(item_type=item_type, item=obj)


@dataclass
class DocStr(ItemBase):
    item: str
    item_type: Literal["blockspace"] = "blockspace"

    @classmethod
    def from_any(cls, item_type: Literal["blockspace"], obj: str):
        return cls(item_type=item_type, item=obj)


__all__ = [
    "DocStr",
    "DocDict",
    "DocTextBlock",
]
