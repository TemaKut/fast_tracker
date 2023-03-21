from pydantic import BaseModel


class DataPerYear(BaseModel):
    """ Схема распределения данных по месяцам в году. """

    january: int | None = None
    february: int | None = None
    march: int | None = None
    april: int | None = None
    may: int | None = None
    june: int | None = None
    july: int | None = None
    august: int | None = None
    september: int | None = None
    october: int | None = None
    november: int | None = None
    december: int | None = None
    amount: int | None = None


class Bdr(BaseModel):
    """ Схема таблицы БДР. """

    incomes: dict[str, DataPerYear] | None = None
    direct_contractors: dict[str, DataPerYear] | None = None
    other_expenses: dict[str, DataPerYear] | None = None
    management_company: dict[str, DataPerYear] | None = None
    incomes_before_tax: dict[str, DataPerYear] | None = None
    ebitda: dict[str, DataPerYear] | None = None
