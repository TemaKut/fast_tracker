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


class BdrCommon(BaseModel):
    """ Схема таблицы БДР. """

    incomes: dict[str, DataPerYear] = {}
    direct_contractors: dict[str, DataPerYear] = {}
    fot_pp: dict[str, DataPerYear] = {}
    fot_aup: dict[str, DataPerYear] = {}
    other_expenses: dict[str, DataPerYear] = {}
    management_company: dict[str, DataPerYear] = {}
    incomes_before_tax: dict[str, DataPerYear] = {}


class Project(BaseModel):
    """ Схема структуры проекта для таблиц по проектам. """
    incomes: dict[str, DataPerYear] | None = None
    expenses: dict[str, DataPerYear] | None = None
    personal: dict[str, DataPerYear] | None = None
