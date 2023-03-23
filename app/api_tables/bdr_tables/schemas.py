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


class DataPerYearWithName(DataPerYear):
    """ Схема данных (Для строки таблицы) с названием месяцами и суммой"""
    name: str | None = None


class Project(BaseModel):
    """ Схема структуры проекта для таблиц по проектам. """
    project_name: str | None = None
    incomes: list[DataPerYearWithName] | None = None
    expenses: list[DataPerYearWithName] | None = None
    personal: list[DataPerYearWithName] | None = None
    amounts: list[DataPerYearWithName] | None = None
