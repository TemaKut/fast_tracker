import json

from ..utils import Tables
from app.utils import tracker_api
from app.settings import log


class CommonWorkingTimeTable(Tables):
    """ Утилиты для получения данных таблицы общ. рабочего времени (План) """

    async def get_data(self, is_plan=True):
        """ Получить данные таблицы планового рабочего времени. """
        # Все подходящие задачи
        issues = await tracker_api.get_list_issues()

        if not issues:
            log.error('Задачи не получены')

        # data -> Общие данные; data_links -> {Имя сотрудника: ключи задач}
        data = {}
        data_links = {}

        for issue in issues:

            try:
                # Есть ли проект
                issue.project.display
                # Находится ли задача в рамках одного года
                await self.is_issue_in_target_year(issue, self.year)

                month = await self.get_target_month(issue)
                full_month = await self.convert_num_month_to_str_month(month)
                staff = issue.assignee.display
                hours = await self.duration_to_work_hours(
                    issue.originalEstimation if is_plan else issue.spent,
                )

                if hours <= 0:
                    continue

                percent = 100 * (hours / self.work_hours_per_month[full_month])

                # Проверка, что задача начата и закончена в одном месяце
                await self.is_start_and_end_within_one_month(issue)

            except Exception:
                continue

            # Добавление ключей задач в список ссылок для каждого сотрудника
            if data_links.get(staff):
                data_links[staff].append(issue.key)
            else:
                data_links[staff] = [issue.key]

            hours_percent = {'hours': hours, 'percent': percent}

            # Если в данных уже есть сотрудник
            if data_staff := data.get(staff):

                # Если ранее записан месяц
                if data_staff.get(full_month):
                    data_staff[full_month]['hours'] += hours
                    data_staff[full_month]['percent'] += hours

                # Если месяца нет
                else:
                    data_staff[full_month] = hours_percent

            # Если в данных нет сотрудника
            else:
                pre_data = {
                    'staff': staff,
                    full_month: hours_percent,
                }
                data[staff] = pre_data

        return await self.add_link_for_staff(data, data_links)

    async def add_link_for_staff(self, data, data_links):
        """ Добавить к основным данным ссылки на используемые задачи. """
        prefix = 'https://tracker.yandex.ru/issues/?key='
        data_links = {key: json.dumps(val) for key, val in data_links.items()}

        for value in data.values():
            data_links_key = value.get('staff')
            value['link'] = prefix + data_links[data_links_key]

        return [values_ for values_ in data.values()]


class WorkingTimeByProjectsTable(Tables):
    """ Методы для формирования таблицы плана общей таблицы Раб.Вр. """

    async def get_data(self, is_plan=True):
        """ Получить данные таблицы  """
        # Все задачи
        issues = await tracker_api.get_list_issues()

        return await self.distribute_issues_by_months(issues, is_plan=is_plan)

    async def distribute_issues_by_months(self, issues, is_plan=True):
        """ Распределить задачи по месяцам. """
        data = {}

        for issue in issues:

            try:
                # Проверка, что задача начата и закончена в одном месяце года
                await self.is_issue_in_target_year(issue, self.year)
                await self.is_start_and_end_within_one_month(issue)

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

            except Exception:
                continue

            hours_percent = {'hours': hours, 'percent': percent}

            # Если в данных был записан месяц
            if d_m := data.get(full_month):

                # Если записан соответствующий сотрудник
                if d_m_s := d_m.get(staff):

                    # Если записан проект
                    if d_m_s_p := d_m_s.get(project):
                        d_m_s_p['hours'] += hours
                        d_m_s_p['percent'] += percent

                        d_m_s['amount_values']['hours'] += hours
                        d_m_s['amount_values']['percent'] += percent

                    # Если проекта нет
                    else:
                        d_m_s[project] = hours_percent
                        d_m_s['amount_values']['hours'] += hours
                        d_m_s['amount_values']['percent'] += percent

                # Если сотрудника нет
                else:
                    d_m[staff] = {
                        project: hours_percent,
                        'amount_values': {'hours': hours, 'percent': percent},
                    }

            # Если в данных нет соответствующего месяца
            else:
                data[full_month] = {
                    staff: {
                        project: hours_percent,
                        'amount_values': {'hours': hours, 'percent': percent},
                    }
                }

            # Добавление сумм для каждого месяца (По проектам)
            if c_a := data[full_month].get('common_amounts'):

                if c_a.get(project):
                    c_a[project] += hours

                else:
                    c_a[project] = hours

            else:
                data[full_month]['common_amounts'] = {project: hours}

        return data
