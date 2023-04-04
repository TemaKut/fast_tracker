import os

from dotenv import load_dotenv

from app.api_company.models import Company
from app.utils import tracker_api
from ..utils import Tables
from .schemas import BdrCommon

# Подгрузить данные из .env
load_dotenv()


class BdrTable(Tables):
    """ Утилиты таблицы БДР (План). """

    async def get_data(self, is_plan=True):
        """ Получить данные таблицы. """
        # Все подходящие задачи
        issues = await tracker_api.get_list_issues()

        # Шаблон данных из схемы
        data = BdrCommon().dict()

        # Объект компании из БД
        company = await Company.get(login=os.getenv('COMPANY_LOGIN'))
        inc_queues = company.incomes_queues
        exp_queues = company.expenses_queues
        salary_queues = company.staff_salary_queues

        for issue in issues:
            try:
                await self.is_issue_end_in_year(
                    issue, self.year, 'end' if is_plan else 'deadline')
                queue = issue.queue.key
                stata_b = issue.stataBudzeta
                tags = issue.tags
                month = await self.get_target_month(
                    issue, 'end' if is_plan else 'deadline'
                )
                full_month = await self.convert_num_month_to_str_month(month)
                summa_etapa = issue.summaEtapa

            except Exception:
                continue

            if not summa_etapa:
                continue

            # Распределение данных по соответствующим ключам в data
            if queue in inc_queues:
                await self.distribute_data(
                    issue, full_month, data, 'incomes',
                )

            elif queue in exp_queues and 'Прямые подрядчики' in stata_b:
                await self.distribute_data(
                    issue, full_month, data, 'direct_contractors',
                )

            elif queue in salary_queues and 'ПП' in tags:
                await self.distribute_data(
                    issue, full_month, data, 'fot_pp',
                )

            elif queue in salary_queues and 'АУП' in tags:
                await self.distribute_data(
                    issue, full_month, data, 'fot_aup',
                )

            elif queue in exp_queues and 'Прочие расходы' in stata_b:
                await self.distribute_data(
                    issue, full_month, data, 'other_expenses',
                )

            elif queue in exp_queues and 'Услуги УК' in stata_b:
                await self.distribute_data(
                    issue, full_month, data, 'management_company',
                )

        return data


class BdrByProjectsTable(Tables):
    """ Утилиты таблицы БДР по проектам (План). """

    async def get_data(self, is_plan=True):
        """ Получить данные таблицы. """
        # Все подходящие задачи
        issues = await tracker_api.get_list_issues()

        return await self.split_issues_by_projects(issues, is_plan=is_plan)

    async def split_issues_by_projects(self, issues, is_plan=True):
        """ Распределить данные из задач по проектам. """
        data = {}
        pesronal_salaryes = await tracker_api.get_personal_salaryes()

        # Объект компании из БД
        company = await Company.get(login=os.getenv('COMPANY_LOGIN'))

        # Список допустимых очередей
        inc_queues = company.incomes_queues
        exp_queues = company.expenses_queues
        team_queues = company.team_queues

        for issue in issues:

            try:
                project_name = issue.project.display
                queue = issue.queue.key
                summary = issue.summary
                summa = issue.summaEtapa  # Допускается None (Для сотрудников)
            except AttributeError:
                continue

            # Принадлежность задачи к той или иной очереди
            inc_issue = None
            exp_issue = None
            staff_issue = None

            try:
                if queue in inc_queues and summa:
                    await self.is_issue_end_in_year(
                        issue, self.year, 'end' if is_plan else 'deadline'
                    )
                    m = await self.get_target_month(
                        issue, 'end' if is_plan else 'deadline'
                    )
                    full_month = await self.convert_num_month_to_str_month(m)
                    inc_issue = issue

                elif queue in exp_queues and summa:
                    await self.is_issue_end_in_year(
                        issue, self.year, 'end' if is_plan else 'deadline'
                    )
                    m = await self.get_target_month(
                        issue, 'end' if is_plan else 'deadline'
                    )
                    full_month = await self.convert_num_month_to_str_month(m)
                    exp_issue = issue

                elif queue in team_queues:
                    await self.is_issue_in_target_year(issue, self.year)
                    await self.is_start_and_end_within_one_month(issue)
                    staff = issue.assignee.display
                    m = await self.get_target_month(issue)
                    full_month = await self.convert_num_month_to_str_month(m)
                    dur = issue.originalEstimation if is_plan else issue.spent
                    hours = await self.duration_to_work_hours(dur)

                    salary = pesronal_salaryes.get(m).get(staff, 0)
                    summa = hours * salary

                    if hours <= 0:
                        continue

                    staff_issue = issue

                else:
                    continue

                if not summa:
                    continue

            except Exception:
                continue

            # Добавить суммы к проекту
            if d_p := data.get(project_name):

                if d_p_a := d_p.get('amounts'):

                    if d_p_a.get(full_month):
                        d_p_a[full_month] += summa

                    else:
                        d_p_a[full_month] = summa

                    d_p_a['amount'] += summa

                else:
                    d_p['amounts'] = {full_month: summa, 'amount': summa}

            else:
                data[project_name] = {
                    'amounts': {full_month: summa, 'amount': summa}
                }

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

                        if d_p_i['amounts'].get(full_month):
                            d_p_i['amounts'][full_month] += summa
                            d_p_i['amounts']['amount'] += summa
                        else:
                            d_p_i['amounts'][full_month] = summa
                            d_p_i['amounts']['amount'] += summa

                    else:
                        d_p['incomes'] = {
                            'amounts': {full_month: summa, 'amount': summa},
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

                        if d_p_i['amounts'].get(full_month):
                            d_p_i['amounts'][full_month] += summa
                            d_p_i['amounts']['amount'] += summa
                        else:
                            d_p_i['amounts'][full_month] = summa
                            d_p_i['amounts']['amount'] += summa

                    else:
                        d_p['expenses'] = {
                            'amounts': {full_month: summa, 'amount': summa},
                            summary: {full_month: summa, 'amount': summa},
                        }

                # Операции с сотрудниками
                if staff_issue:

                    if d_p_p := d_p.get('personal'):

                        if d_p_p_s := d_p_p.get(staff):

                            if d_p_p_s.get(full_month):
                                d_p_p_s[full_month]['hours'] += hours
                                d_p_p_s[full_month]['salary'] += summa
                                d_p_p_s['amount_hours'] += hours
                                d_p_p_s['amount_salary'] += summa

                            else:
                                d_p_p_s[full_month] = {
                                    'hours': hours,
                                    'salary': summa,
                                }

                                d_p_p_s['amount_hours'] += hours
                                d_p_p_s['amount_salary'] += summa

                        else:
                            d_p_p[staff] = {
                                full_month: {
                                    'hours': hours,
                                    'salary': summa,
                                },
                                'amount_hours': hours,
                                'amount_salary': summa,
                            }

                        if d_p_p['amounts'].get(full_month):
                            d_p_p['amounts'][full_month] += summa
                            d_p_p['amounts']['amount'] += summa
                        else:
                            d_p_p['amounts'][full_month] = summa
                            d_p_p['amounts']['amount'] += summa

                    else:
                        d_p['personal'] = {
                            'amounts': {full_month: summa, 'amount': summa},
                            staff: {
                                full_month: {
                                    'hours': hours,
                                    'salary': summa,
                                },
                                'amount_hours': hours,
                                'amount_salary': summa,
                            }
                        }

            # Если в данных нет информации о проекте
            else:
                # Положить данные доходов | расходов в проект (Полный путь)
                data[project_name] = {
                    'incomes': {
                        'amounts': {full_month: summa, 'amount': summa},
                        summary: {full_month: summa, 'amount': summa},
                    } if inc_issue else None,
                    'expenses': {
                        'amounts': {full_month: summa, 'amount': summa},
                        summary: {full_month: summa, 'amount': summa},
                    } if exp_issue else None,
                }

                # Положить данные сотрудника в проект (Полный путь)
                # ..Если задачу можно характеризовать как сотрудническую
                if staff_issue:
                    data[project_name]['personal'] = {
                        'amounts': {full_month: summa, 'amount': summa},
                        staff: {
                            full_month: {
                                'hours': hours,
                                'salary': summa,
                            },
                            'amount_hours': hours,
                            'amount_salary': summa,
                        }
                    }

        return data
