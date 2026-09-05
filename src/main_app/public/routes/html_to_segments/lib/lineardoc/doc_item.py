""" """

from __future__ import annotations

from dataclasses import dataclass
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
    def load(cls, item_type: str, obj: TextBlock):
        return cls(item_type=item_type, item=obj)

    def generate_textblock_xml(self, pad: str = "") -> list[str]:
        dump = [f"{pad}<cxtextblock>"]
        dump.extend(self.item.dump_xml_array(pad + "  "))
        dump.append(f"{pad}</cxtextblock>")

        return dump


@dataclass
class DictTag:
    name: str
    attributes: dict[str, Any]

    def __getitem__(self, key: str) -> str | dict[str, Any]:
        # connect keys to object properties
        if key == "name":
            return self.name
        elif key == "attributes":
            return self.attributes
        else:
            raise KeyError(f"key '{key}' not found in dict tag")


class DocDict(ItemBase):
    item_type: ITEM_TYPES_STR
    item: DictTag

    @classmethod
    def load(cls, item_type: ITEM_TYPES_STR, obj: dict[str, Any]):
        """
        Args:
            item_type: Literal["open", "close"]
            obj: Tag dict with 'name' and 'attributes'
        """
        item_obj = DictTag(name=obj["name"], attributes=obj["attributes"])
        return cls(item_type=item_type, item=item_obj)

    def opening_tag(self, pad: str = "") -> str:
        return f"{pad}<{self.item.name}>"

    def closing_tag(self, pad: str = "") -> str:
        return f"{pad}</{self.item.name}>"


@dataclass
class DocStr(ItemBase):
    item: str
    item_type: Literal["blockspace"] = "blockspace"

    @classmethod
    def load(cls, obj: str):
        return cls(item=obj)


__all__ = [
    "DocStr",
    "DocDict",
    "DocTextBlock",
]
