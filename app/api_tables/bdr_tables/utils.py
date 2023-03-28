from app.settings import log
from app.settings import settings as s
from app.utils import tracker_api
from ..utils import Tables
from .schemas import BdrCommon


class BdrPlanTable(Tables):
    """ Утилиты таблицы БДР (План). """

    async def get_data(self):
        """ Получить данные таблицы. """
        # Все подходящие задачи
        issues = await self.get_issues()

        # Шаблон данных из схемы
        data = BdrCommon().dict()

        for issue in issues:
            queue = issue.queue.key
            stata_b = issue.stataBudzeta
            tags = issue.tags

            # Распределение данных по соответствующим ключам в data
            if queue in s.INCOMES_QUEUES:
                await self.distribute_data(
                    issue, data, 'incomes',
                )

            elif queue in s.EXPENSES_QUEUES and 'Прямые подрядчики' in stata_b:
                await self.distribute_data(
                    issue, data, 'direct_contractors',
                )

            elif queue in s.STAFF_SALARY_QUEUES and 'ПП' in tags:
                await self.distribute_data(
                    issue, data, 'fot_pp',
                )

            elif queue in s.STAFF_SALARY_QUEUES and 'АУП' in tags:
                await self.distribute_data(
                    issue, data, 'fot_aup',
                )

            elif queue in s.EXPENSES_QUEUES and 'Прочие расходы' in stata_b:
                await self.distribute_data(
                    issue, data, 'other_expenses',
                )

            elif queue in s.EXPENSES_QUEUES and 'Услуги УК' in stata_b:
                await self.distribute_data(
                    issue, data, 'management_company',
                )

        return data

    async def get_issues(self):
        """ Получить все нужные задачи. """
        # Все очереди
        all_issues = await tracker_api.get_list_issues()

        # Список допустимых очередей
        queues = s.INCOMES_QUEUES + s.EXPENSES_QUEUES + s.STAFF_SALARY_QUEUES

        filter_ = {
            'issue.queue.key': queues,
            'issue.summaEtapa != 0': True,
            'issue.end.split("-")[0]': str(self.year),
        }

        # Из общего списка задач фильтровать нужные
        issues = await self.get_target_issues(all_issues, filter_)

        if not issues:
            log.error('Задачи не были получены после фильтрации.')

        return issues

    async def distribute_data(self, issue, data, key) -> None:
        """
        Метод распределения данных из задачи по объекту словаря.
        Метод получает объект словаря и изменяет его, ничего не возвращая.
        """
        try:
            data[key]

        except KeyError:
            log.critical('Такого ключа в словаре нет.')
            raise KeyError(f'Такого ключа в словаре нет. ({key})')

        month = await self.get_target_month(issue)
        full_month = await self.convert_num_month_to_str_month(month)
        name = issue.summary
        summa_etapa = issue.summaEtapa

        if not summa_etapa:
            return

        # Распределение данных О(n)
        # Если в data.get(key) уже есть name
        if data_n := data[key].get(name):

            # Если ранее записан месяц
            if data_n.get(full_month):
                data_n[full_month] += summa_etapa
                data_n['amount'] += summa_etapa

            # Если месяца в данных нет
            else:
                data_n[full_month] = summa_etapa
                data_n['amount'] += summa_etapa

        # Если в data.get(key) нет name
        else:
            data[key][name] = {full_month: summa_etapa, 'amount': summa_etapa}

        # Распределение сумм
        if amounts := data[key].get('amounts'):
            if amounts.get(full_month):
                amounts[full_month] += summa_etapa
                amounts['amount'] += summa_etapa
            else:
                amounts[full_month] = summa_etapa
                amounts['amount'] += summa_etapa

        else:
            data[key]['amounts'] = {
                full_month: summa_etapa,
                'amount': summa_etapa,
            }


class BdrFactTable(BdrPlanTable):
    """ Утилиты таблицы БДР (Факт). """

    async def get_issues(self):
        """ Получить все нужные задачи. """
        # Все задачи
        all_issues = await tracker_api.get_list_issues()

        # Допустимые очереди
        queues = s.INCOMES_QUEUES + s.EXPENSES_QUEUES + s.STAFF_SALARY_QUEUES

        filter_ = {
            'issue.queue.key': queues,
            'issue.summaEtapa != 0': True,
            'issue.deadline.split("-")[0]': str(self.year),
        }

        # Из общего списка задач фильтровать нужные
        issues = await self.get_target_issues(all_issues, filter_)

        if not issues:
            log.error('Задачи не были получены после фильтрации.')

        return issues

    async def get_target_month(self, issue, target_: str = 'deadline'):
        """ Получить целевой месяц задачи. (Переопределение на deadline). """

        return await super().get_target_month(issue, target_)


class BdrByProjectsPlan(Tables):
    """ Утилиты таблицы БДР по проектам (План). """

    async def get_data(self, is_plan=True):
        """ Получить данные таблицы. """
        # Все подходящие задачи
        issues = await tracker_api.get_list_issues()

        return await self.split_issues_by_projects(issues, is_plan=is_plan)

    async def get_issues(self):
        """ Получить все нужные задачи. """
        # Все задачи
        all_issues = await tracker_api.get_list_issues()

        # Допустимые очереди
        queues = s.INCOMES_QUEUES + s.EXPENSES_QUEUES + s.TEAMS_QUEUES

        filter_ = {
            'issue.queue.key': queues,
            'bool(issue.project)': True,
            'bool(issue.queue)': True,
        }

        # Из общего списка задач фильтровать нужные
        issues = await self.get_target_issues(all_issues, filter_)

        if not issues:
            log.error('Задачи не были получены после фильтрации.')

        return issues

    async def split_issues_by_projects(self, issues, is_plan=True):
        """ Распределить данные из задач по проектам. """
        data = {}
        pesronal_salaryes = await tracker_api.get_personal_salaryes()

        for issue in issues:

            # Проверка наличия необходимых аттрибутов у задачи
            try:
                project_name = issue.project.display
                queue = issue.queue.key
                summary = issue.summary
                summa = issue.summaEtapa  # Допускается None (Для сотрудников)
                staff = issue.assignee.display

            except AttributeError:
                continue

            # Принадлежность задачи к той или иной очереди
            inc_issue = None
            exp_issue = None
            staff_issue = None
            try:
                if queue in s.INCOMES_QUEUES and summa:
                    m = await self.get_target_month(
                        issue, 'end' if is_plan else 'deadline'
                    )
                    full_month = await self.convert_num_month_to_str_month(m)
                    inc_issue = issue

                elif queue in s.EXPENSES_QUEUES and summa:
                    m = await self.get_target_month(
                        issue, 'end' if is_plan else 'deadline'
                    )
                    full_month = await self.convert_num_month_to_str_month(m)
                    exp_issue = issue

                elif queue in s.TEAMS_QUEUES:
                    m = await self.get_target_month(issue)
                    full_month = await self.convert_num_month_to_str_month(m)
                    staff_issue = issue
                    dur = issue.originalEstimation if is_plan else issue.spent

                    if not isinstance(dur, str):
                        continue

                    try:
                        salary = pesronal_salaryes.get(m).get(staff, 0)

                    except AttributeError:
                        salary = 0
            except Exception:
                continue

            # Распределение данных за O(n)
            # Если в данных есть информация о проекте
            if d_p := data.get(project_name):

                # Операции с доходами
                if inc_issue:

                    if d_p_i := d_p.get('incomes'):

                        if d_p_i_s := d_p_i.get(summary):

                            if d_p_i_s_fm := d_p_i_s.get(full_month):
                                d_p_i_s_fm += summa
                                d_p_i_s['amount'] += summa

                            else:
                                d_p_i_s[full_month] = summa
                                d_p_i_s['amount'] += summa

                        else:
                            d_p_i[summary] = {
                                full_month: summa, 'amount': summa,
                            }

                    else:
                        d_p['incomes'] = {
                            summary: {full_month: summa, 'amount': summa},
                        }

                # Операции с расходами
                if exp_issue:

                    if d_p_i := d_p.get('expenses'):

                        if d_p_i_s := d_p_i.get(summary):

                            if d_p_i_s_fm := d_p_i_s.get(full_month):
                                d_p_i_s_fm += summa
                                d_p_i_s['amount'] += summa

                            else:
                                d_p_i_s[full_month] = summa
                                d_p_i_s['amount'] += summa

                        else:
                            d_p_i[summary] = {
                                full_month: summa, 'amount': summa,
                            }

                    else:
                        d_p['expenses'] = {
                            summary: {full_month: summa, 'amount': summa},
                        }

                # Операции с сотрудниками
                if staff_issue:
                    hours = await self.duration_to_work_hours(dur)
                    salary = hours * salary

                    if hours <= 0:
                        continue

                    if d_p_p := d_p.get('personal'):

                        if d_p_p_s := d_p_p.get(staff):

                            if d_p_p_s.get(full_month):
                                d_p_p_s[full_month]['hours'] += hours
                                d_p_p_s[full_month]['salary'] += salary
                                d_p_p_s['amount_hours'] += hours
                                d_p_p_s['amount_salary'] += salary

                            else:
                                d_p_p_s[full_month] = {
                                    'hours': hours,
                                    'salary': salary,
                                }

                                d_p_p_s['amount_hours'] += hours
                                d_p_p_s['amount_salary'] += salary

                        else:
                            d_p_p[staff] = {
                                full_month: {
                                    'hours': hours,
                                    'salary': salary,
                                },
                                'amount_hours': hours,
                                'amount_salary': salary,
                            }

                    else:
                        d_p['personal'] = {
                            staff: {
                                full_month: {
                                    'hours': hours,
                                    'salary': salary,
                                },
                                'amount_hours': hours,
                                'amount_salary': salary,
                            }
                        }

            # Если в данных нет информации о проекте
            else:
                # Положить данные доходов | расходов в проект (Полный путь)
                data[project_name] = {
                    'incomes': {
                        summary: {full_month: summa, 'amount': summa},
                    } if inc_issue else {},
                    'expenses': {
                        summary: {full_month: summa, 'amount': summa},
                    } if exp_issue else {},
                }

                # Положить данные сотрудника в проект (Полный путь)
                # ..Если задачу можно характеризовать как сотрудническую
                if staff_issue:
                    hours = await self.duration_to_work_hours(dur)
                    salary = hours * salary

                    if hours <= 0:
                        continue

                    data[project_name]['personal'] = {
                        staff: {
                            full_month: {
                                'hours': hours,
                                'salary': salary,
                            },
                            'amount_hours': hours,
                            'amount_salary': salary,
                        }
                    }

        return data

    async def get_target_month(self, issue, target_: str = 'end'):
        """ Получить целевой месяц задачи. """
        if target_ not in ['end', 'deadline']:
            log.error('target_ -> in ["end", "deadline"]')
            raise ValueError('target_ -> in ["end", "deadline"]')

        if target_ == 'end':

            if issue.end.split("-")[0] != str(self.year):
                raise ValueError('Не подходящая по году задача')

            return issue.end.split("-")[1]

        if issue.deadline.split("-")[0] != str(self.year):
            raise ValueError('Не подходящая по году задача')

        return issue.deadline.split("-")[1]


class BdrByProjectsFact(BdrByProjectsPlan):
    """ Утилиты таблицы БДР по проектам (Факт). """

    pass
