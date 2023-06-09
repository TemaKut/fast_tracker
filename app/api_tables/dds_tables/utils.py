import os

from dotenv import load_dotenv

from app.api_company.models import Company
from app.utils import tracker_api
from ..utils import Tables
from .schemas import DdsCommon

# Подгрузить данные из .env
load_dotenv()


class DdsTable(Tables):
    """ Утилиты таблицы ДДС (План). """

    async def get_data(self, is_plan=True):
        """ Получить данные таблицы. """
        # Все подходящие задачи
        issues = await tracker_api.get_list_issues()

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
            try:
                await self.is_issue_end_in_year(
                    issue, self.year, 'end' if is_plan else 'deadline')
                queue = issue.queue.key
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

            # Распределение данных по соответствующим признакам в data
            if queue in rec_queues:
                await self.distribute_data(
                    issue, full_month, data, 'incomes',
                )

            elif queue in pay_queues and 'Текущий_подрядчик' in tags:
                await self.distribute_data(
                    issue, full_month, data, 'direct_contractors',
                )

            elif queue in pay_queues and 'Агентские_платежи' in tags:
                await self.distribute_data(
                    issue, full_month, data, 'agency_payments',
                )

            elif queue in pay_queues and 'Зарплата' in tags:
                await self.distribute_data(
                    issue, full_month, data, 'salaries',
                )

            elif queue in pay_queues and 'Бонусный_фонд' in tags:
                await self.distribute_data(
                    issue, full_month, data, 'bonus_fund',
                )

            elif queue in tax_queues and 'Налог_НДФЛ_/_Соцстрах' in tags:
                await self.distribute_data(
                    issue, full_month, data, 'tax_ndfl',
                )

            elif queue in tax_queues and 'Налог_НДС' in tags:
                await self.distribute_data(
                    issue, full_month, data, 'tax_nds',
                )

            elif queue in tax_queues and 'Налог_на_прибыль' in tags:
                await self.distribute_data(
                    issue, full_month, data, 'tax_income',
                )

            elif queue in pay_queues and 'Пени_по_налогам' in tags:
                await self.distribute_data(
                    issue, full_month, data, 'tax_penalties',
                )

            elif queue in pay_queues and 'Услуги_УК' in tags:
                await self.distribute_data(
                    issue, full_month, data, 'management_company',
                )

            elif queue in pay_queues and 'Прочие_расходы' in tags:
                await self.distribute_data(
                    issue, full_month, data, 'other_expenses',
                )

            elif queue in pay_queues and 'Судебные_взыскания_\_Штрафы' in tags:
                await self.distribute_data(
                    issue, full_month, data, 'judicial_penalties',
                )

            elif queue in pay_queues and 'Старые_подрядчики' in tags:
                await self.distribute_data(
                    issue, full_month, data, 'old_contractors',
                )

            elif queue in pay_queues and 'Займы_акционеров' in tags:
                await self.distribute_data(
                    issue, full_month, data, 'loans_shareholders',
                )

            elif queue in pay_queues and 'Процент_по_займам' in tags:
                await self.distribute_data(
                    issue, full_month, data, 'interest_on_loans',
                )

        return data


class DdsByProjects(Tables):
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
                await self.is_issue_end_in_year(
                    issue, self.year, 'end' if is_plan else 'deadline'
                )
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
            # Добавление общей суммы
            if inc_issue or exp_issue:

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

        return data
