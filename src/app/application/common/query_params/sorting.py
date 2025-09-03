from dataclasses import dataclass
from enum import StrEnum


class SortingOrder(StrEnum):
    ASC = "ASC"
    DESC = "DESC"


@dataclass(frozen=True, slots=True, kw_only=True)
class Sorting:
    sorting_field: str
    sorting_order: SortingOrder
