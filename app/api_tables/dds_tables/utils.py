import os

from dotenv import load_dotenv

from app.api_company.models import Company
from app.settings import log
from app.utils import tracker_api
from ..bdr_tables.utils import BdrPlanTable
from ..utils import Tables
from .schemas import DdsCommon

# Подгрузить данные из .env
load_dotenv()


class DdsPlanTable(BdrPlanTable):
    """ Утилиты таблицы ДДС (План). """

    async def get_data(self):
        """ Получить данные таблицы. """
        # Все подходящие задачи
        issues = await self.get_issues()

        # Объект компании из БД
        company = await Company.get(login=os.getenv('COMPANY_LOGIN'))

        # Список допустимых очередей
        rec_queues = company.receipts_queues
        pay_queues = company.payments_queues
        tax_queues = company.tax_queues

        # Шаблон данных из схемы в виде словаря
        data = DdsCommon()
        data = data.dict()

        for issue in issues:
            queue = issue.queue.key
            tags = issue.tags

            # Распределение данных по соответствующим признакам в data
            if queue in rec_queues:
                await self.distribute_data(issue, data, 'incomes')

            elif queue in pay_queues and 'Текущий_подрядчик' in tags:
                await self.distribute_data(issue, data, 'direct_contractors')

            elif queue in pay_queues and 'Агентские_платежи' in tags:
                await self.distribute_data(issue, data, 'agency_payments')

            elif queue in pay_queues and 'Зарплата' in tags:
                await self.distribute_data(issue, data, 'salaries')

            elif queue in pay_queues and 'Бонусный_фонд' in tags:
                await self.distribute_data(issue, data, 'bonus_fund')

            elif queue in tax_queues and 'Налог_НДФЛ_/_Соцстрах' in tags:
                await self.distribute_data(issue, data, 'tax_ndfl')

            elif queue in tax_queues and 'Налог_НДС' in tags:
                await self.distribute_data(issue, data, 'tax_nds')

            elif queue in tax_queues and 'Налог_на_прибыль' in tags:
                await self.distribute_data(issue, data, 'tax_income')

            elif queue in pay_queues and 'Пени_по_налогам' in tags:
                await self.distribute_data(issue, data, 'tax_penalties')

            elif queue in pay_queues and 'Услуги_УК' in tags:
                await self.distribute_data(issue, data, 'management_company')

            elif queue in pay_queues and 'Прочие_расходы' in tags:
                await self.distribute_data(issue, data, 'other_expenses')

            elif queue in pay_queues and 'Судебные_взыскания_\_Штрафы' in tags:
                await self.distribute_data(issue, data, 'judicial_penalties')

            elif queue in pay_queues and 'Старые_подрядчики' in tags:
                await self.distribute_data(issue, data, 'old_contractors')

            elif queue in pay_queues and 'Займы_акционеров' in tags:
                await self.distribute_data(issue, data, 'loans_shareholders')

            elif queue in pay_queues and 'Проценты_по_займам' in tags:
                await self.distribute_data(issue, data, 'interest_on_loans')

        return data

    async def get_issues(self):
        """ Получить все нужные задачи. """
        # Все задачи
        all_issues = await tracker_api.get_list_issues()

        # Объект компании из БД
        company = await Company.get(login=os.getenv('COMPANY_LOGIN'))

        # Допустимые очереди
        queues = (
            company.receipts_queues
            + company.payments_queues
            + company.tax_queues
        )

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


class DdsFactTable(DdsPlanTable):
    """ Утилиты таблицы ДДС (Факт). """

    async def get_issues(self):
        """ Получить все нужные задачи. """
        # Все задачи
        all_issues = await tracker_api.get_list_issues()

        # Объект компании из БД
        company = await Company.get(login=os.getenv('COMPANY_LOGIN'))

        # Допустимые очереди
        queues = (
            company.receipts_queues
            + company.payments_queues
            + company.tax_queues
        )

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
        """ Получить целевой месяц задачи. (Переопределение на deadline) """

        return await super().get_target_month(issue, target_)


class DdsByProjectsPlan(Tables):
    """ Утилиты таблицы ДДС по проектам (План). """

    async def get_data(self, is_plan=True):
        """ Получить данные таблицы. """
        # Все подходящие задачи
        issues = await tracker_api.get_list_issues()

        return await self.split_issues_by_projects(issues, is_plan=is_plan)

    async def split_issues_by_projects(self, issues, is_plan=True):
        """ Распределить данные из задач по проектам. """
        data = {}
        # Объект компании из БД
        company = await Company.get(login=os.getenv('COMPANY_LOGIN'))

        # Допустимые очереди
        rec_queues = company.receipts_queues
        pay_queues = company.payments_queues
        tax_queues = company.tax_queues

        for issue in issues:

            # Проверка наличия необходимых аттрибутов у задачи
            try:
                project_name = issue.project.display
                queue = issue.queue.key
                summary = issue.summary
                summa = issue.summaEtapa
                month = await self.get_target_month(
                    issue, 'end' if is_plan else 'deadline'
                )
                full_month = await self.convert_num_month_to_str_month(month)
            except Exception:
                continue

            # Принадлежность задачи к той или иной очереди
            inc_issue = issue if queue in rec_queues and summa else None

            exp_queues = pay_queues + tax_queues
            exp_issue = issue if queue in exp_queues and summa else None

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


class DdsByProjectsFact(DdsByProjectsPlan):
    """ Утилиты таблицы ДДС по проектам (Факт). """

    async def get_data(self, is_plan=False):
        """ Получить данные таблицы. """
        # Все подходящие задачи
        issues = await tracker_api.get_list_issues()

        return await self.split_issues_by_projects(issues, is_plan=is_plan)
