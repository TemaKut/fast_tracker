from app.api_tables.utils.tables import Tables
from app.source_tracker_api.utils import tracker_api
from ..schemas import WorkingTime


class CommonWorkingTimeTable(Tables):
    """ Методы для формирования таблицы плана общей таблицы Раб.Вр. """

    def __init__(self, year):
        """ Инициализация класса. """
        super().__init__()
        self.year = year

    async def get_data(self):
        """ Получить данные таблицы планового рабочего времени. """
        all_issues = await tracker_api.get_list_issues()

        # Из общего списка задач фильтровать нужные
        issues = await self.get_target_issues(
            all_issues,
            {
                'bool(issue.assignee.display)': True,
                'bool(issue.project.display)': True,
                'bool(issue.originalEstimation)': True,
                'issue.start.split("-")[0]': str(self.year),
                'issue.end.split("-")[0]': str(self.year),
            },
        )

        data = {}

        for issue in issues:

            try:
                month = await self.get_target_month(issue)
                full_month = await self.convert_num_month_to_str_month(month)
                staff = issue.assignee.display
                hours = await self.duration_to_work_hours(
                    issue.originalEstimation,
                )

                if hours <= 0:
                    continue

                # Проверка, что задача начата и закончена в одном месяце
                await self.is_start_and_end_within_one_month(issue)

            except Exception:
                continue

            if data_staff := data.get(staff):

                if data_staff.get(full_month):
                    data_staff[full_month] += hours
                else:
                    data_staff[full_month] = hours

            else:
                pre_data = {
                    'staff': staff,
                    full_month: hours,
                }
                data[staff] = pre_data

        data_with_percent = await self.add_percent_to_hours(data.values())

        data = [WorkingTime(**values) for values in data_with_percent]

        return data


class WorkingTimeByProjectsTable(Tables):
    """ Методы для формирования таблицы плана общей таблицы Раб.Вр. """

    def __init__(self, year):
        """ Инициализация класса. """
        super().__init__()
        self.year = year

    async def get_data(self):
        """ Получить данные таблицы  """
        all_issues = await tracker_api.get_list_issues()

        # Из общего списка задач фильтровать нужные
        issues = await self.get_target_issues(
            all_issues,
            {
                'bool(issue.assignee.display)': True,
                'bool(issue.project.display)': True,
                'bool(issue.originalEstimation)': True,
                'issue.start.split("-")[0]': str(self.year),
                'issue.end.split("-")[0]': str(self.year),
            },
        )

        return await self.distribute_issues_by_months(issues)

    async def distribute_issues_by_months(self, issues, is_plan=True):
        """ Распределить задачи по месяцам. """
        data = {}

        for issue in issues:

            try:
                month = await self.get_target_month(issue)
                full_month = await self.convert_num_month_to_str_month(month)
                staff = issue.assignee.display
                project = issue.project.display
                hours = await self.duration_to_work_hours(
                    issue.originalEstimation if is_plan else issue.spent,
                )
                percent = 100 * (hours / self.work_hours_per_month[full_month])

                if hours <= 0:
                    continue

                # Проверка, что задача начата и закончена в одном месяце
                await self.is_start_and_end_within_one_month(issue)

            except Exception:
                continue

            hours_percent = {'hours': hours, 'percent': percent}

            if d_m := data.get(full_month):

                if d_m_s := d_m.get(staff):

                    if d_m_s_p := d_m_s.get(project):
                        d_m_s_p['hours'] += hours
                        d_m_s_p['percent'] += percent

                    else:
                        d_m_s[project] = hours_percent

                else:
                    d_m[staff] = {project: hours_percent}

            else:
                data[full_month] = {staff: {project: hours_percent}}

        return data


class WorkingTimeByProjectsFactTable(WorkingTimeByProjectsTable):
    """ Методы для формирования таблицы факта общей таблицы Раб.Вр. """

    async def get_data(self):
        """ Получить данные таблицы  """
        all_issues = await tracker_api.get_list_issues()

        # Из общего списка задач фильтровать нужные
        issues = await self.get_target_issues(
            all_issues,
            {
                'bool(issue.assignee.display)': True,
                'bool(issue.project.display)': True,
                'bool(issue.spent)': True,
                'issue.start.split("-")[0]': str(self.year),
                'issue.end.split("-")[0]': str(self.year),
            },
        )

        return await self.distribute_issues_by_months(issues)

    async def distribute_issues_by_months(self, issues):
        """ Распределить задачи по месяцам. """
        res = await super().distribute_issues_by_months(issues, is_plan=False)

        return res
