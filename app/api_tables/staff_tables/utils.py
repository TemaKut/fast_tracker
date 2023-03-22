from ..utils import Tables
from app.utils import tracker_api
from .schemas import WorkingTime
from app.settings import log


class CommonWorkingTimePlanTable(Tables):
    """ Утилиты для получения данных таблицы общ. рабочего времени (План) """

    async def get_data(self, is_plan=True):
        """ Получить данные таблицы планового рабочего времени. """
        issues = await self.get_issues_for_table()

        if not issues:
            log.error('Задачи не получены')

        data = {}

        for issue in issues:

            try:
                month = await self.get_target_month(issue)
                full_month = await self.convert_num_month_to_str_month(month)
                staff = issue.assignee.display
                hours = await self.duration_to_work_hours(
                    issue.originalEstimation if is_plan else issue.spent,
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

    async def get_issues_for_table(self):
        """ Получить целевые задачи. """
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

        return issues


class CommonWorkingTimeFactTable(CommonWorkingTimePlanTable):
    """ Утилиты для получения данных таблицы общего рабочего времени (Факт) """

    async def get_issues_for_table(self):
        """ Получить целевые задачи. """
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

        return issues
    
    async def get_data(self, is_plan=False):
        """ Получить данные таблицы планового рабочего времени. """

        return await super().get_data(is_plan)


class WorkingTimeByProjectsTable(Tables):
    """ Методы для формирования таблицы плана общей таблицы Раб.Вр. """

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

        if not issues:
            log.error('Задачи не получены')

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
                        d_m_s['amount_hours'] += hours

                    else:
                        d_m_s[project] = hours_percent
                        d_m_s['amount_hours'] += hours

                else:
                    d_m[staff] = {
                        project: hours_percent,
                        'amount_hours': hours,
                    }

            else:
                data[full_month] = {
                    staff: {project: hours_percent, 'amount_hours': hours},
                }

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

        if not issues:
            log.error('Задачи не получены')

        return await self.distribute_issues_by_months(issues)

    async def distribute_issues_by_months(self, issues):
        """ Распределить задачи по месяцам. """
        res = await super().distribute_issues_by_months(issues, is_plan=False)

        return res
