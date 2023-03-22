from pydantic import BaseModel


class HoursPercent(BaseModel):
    """ Рабочие часы и % от месячной нормы. """
    hours: int
    percent: int


class WorkingTime(BaseModel):
    """ Месяц с указанием рабочих часов. """

    staff: str = None
    january: HoursPercent | None = None
    february: HoursPercent | None = None
    march: HoursPercent | None = None
    april: HoursPercent | None = None
    may: HoursPercent | None = None
    june: HoursPercent | None = None
    july: HoursPercent | None = None
    august: HoursPercent | None = None
    september: HoursPercent | None = None
    october: HoursPercent | None = None
    november: HoursPercent | None = None
    december: HoursPercent | None = None


class WorkingTimeByMonthAndProjects(BaseModel):
    """
    Структура данных где по месяцам и проектам
    разделены рабочие часы сотрудников
    """

    january: dict[str, dict[str, HoursPercent | int]] | None = None
    february: dict[str, dict[str, HoursPercent | int]] | None = None
    march: dict[str, dict[str, HoursPercent | int]] | None = None
    april: dict[str, dict[str, HoursPercent | int]] | None = None
    may: dict[str, dict[str, HoursPercent | int]] | None = None
    june: dict[str, dict[str, HoursPercent | int]] | None = None
    july: dict[str, dict[str, HoursPercent | int]] | None = None
    august: dict[str, dict[str, HoursPercent | int]] | None = None
    september: dict[str, dict[str, HoursPercent | int]] | None = None
    october: dict[str, dict[str, HoursPercent | int]] | None = None
    november: dict[str, dict[str, HoursPercent | int]] | None = None
    december: dict[str, dict[str, HoursPercent | int]] | None = None
