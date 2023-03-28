from pydantic import BaseModel

from ..bdr_tables.schemas import DataPerYear


class DdsCommon(BaseModel):
    """ Схема данных общей таблицы ДДС """

    incomes: dict[str, DataPerYear] = {}
    direct_contractors: dict[str, DataPerYear] = {}
    agency_payments: dict[str, DataPerYear] = {}
    salaries: dict[str, DataPerYear] = {}
    bonus_fund: dict[str, DataPerYear] = {}
    tax_ndfl: dict[str, DataPerYear] = {}
    tax_nds: dict[str, DataPerYear] = {}
    tax_income: dict[str, DataPerYear] = {}
    tax_penalties: dict[str, DataPerYear] = {}
    management_company: dict[str, DataPerYear] = {}
    other_expenses: dict[str, DataPerYear] = {}
    judicial_penalties: dict[str, DataPerYear] = {}
    old_contractors: dict[str, DataPerYear] = {}
    loans_shareholders: dict[str, DataPerYear] = {}
    interest_on_loans: dict[str, DataPerYear] = {}


class Project(BaseModel):
    """ Схема структуры проекта для таблиц по проектам. """
    incomes: dict[str, DataPerYear] | None = None
    expenses: dict[str, DataPerYear] | None = None
