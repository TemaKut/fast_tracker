from pydantic import BaseModel


class HoursPercent(BaseModel):
    """ Рабочие часы и % от месячной нормы. """
    hours: int
    percent: int


class WorkingTime(BaseModel):
    """ Месяц с указанием рабочих часов. """

    name: str = None
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
