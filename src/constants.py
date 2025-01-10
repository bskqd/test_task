import enum
import functools


class PaymentTypeEnum(enum.Enum):
    cash = "cash"
    card = "card"

    @classmethod
    @functools.lru_cache(maxsize=1)
    def _display_name_mapping(cls) -> dict:
        return {cls.cash: "Готівка", cls.card: "Картка"}

    @classmethod
    def get_display_name(cls, value_to_display: str) -> str:
        return cls._display_name_mapping().get(value_to_display, "")
