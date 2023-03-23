from app.settings import log
from app.settings import settings as s
from app.utils import tracker_api
from ..bdr_tables.utils import BdrPlanTable
from .schemas import DdsCommon


class DdsPlanTable(BdrPlanTable):
    """ Утилиты таблицы ДДС (План). """

    async def get_data(self):
        """ Получить данные таблицы. """
        issues = await self.get_issues()

        data = DdsCommon()
        data = data.dict()

        for issue in issues:
            queue = issue.queue.key
            tags = issue.tags

            if queue in s.RECEIPTS_QUEUES:
                await self.distribute_data(issue, data, 'incomes')

            elif queue in s.PAYMENTS_QUEUES and 'Текущий_подрядчик' in tags:
                await self.distribute_data(issue, data, 'direct_contractors')

            elif queue in s.PAYMENTS_QUEUES and 'Агентские_платежи' in tags:
                await self.distribute_data(issue, data, 'agency_payments')

            elif queue in s.PAYMENTS_QUEUES and 'Зарплата' in tags:
                await self.distribute_data(issue, data, 'salaries')

            elif queue in s.PAYMENTS_QUEUES and 'Бонусный_фонд' in tags:
                await self.distribute_data(issue, data, 'bonus_fund')

            elif queue in s.TAX_QUEUES and 'Налог_НДФЛ_/_Соцстрах' in tags:
                await self.distribute_data(issue, data, 'tax_ndfl')

            elif queue in s.TAX_QUEUES and 'Налог_НДС' in tags:
                await self.distribute_data(issue, data, 'tax_nds')

            elif queue in s.TAX_QUEUES and 'Налог_на_прибыль' in tags:
                await self.distribute_data(issue, data, 'tax_income')

            elif queue in s.PAYMENTS_QUEUES and 'Пени_по_налогам' in tags:
                await self.distribute_data(issue, data, 'tax_penalties')

            elif queue in s.PAYMENTS_QUEUES and 'Услуги_УК' in tags:
                await self.distribute_data(issue, data, 'management_company')

            elif queue in s.PAYMENTS_QUEUES and 'Прочие_расходы' in tags:
                await self.distribute_data(issue, data, 'other_expenses')

            elif (
                queue in s.PAYMENTS_QUEUES
                and 'Судебные_взыскания_\_Штрафы' in tags
            ):
                await self.distribute_data(issue, data, 'judicial_penalties')

            elif queue in s.PAYMENTS_QUEUES and 'Старые_подрядчики' in tags:
                await self.distribute_data(issue, data, 'old_contractors')

            elif queue in s.PAYMENTS_QUEUES and 'Займы_акционеров' in tags:
                await self.distribute_data(issue, data, 'loans_shareholders')

            elif queue in s.PAYMENTS_QUEUES and 'Проценты_по_займам' in tags:
                await self.distribute_data(issue, data, 'interest_on_loans')

        return data

    async def get_issues(self):
        """ Получить все нужные задачи. """
        all_issues = await tracker_api.get_list_issues()

        queues = s.RECEIPTS_QUEUES + s.PAYMENTS_QUEUES + s.TAX_QUEUES

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
        all_issues = await tracker_api.get_list_issues()

        queues = s.RECEIPTS_QUEUES + s.PAYMENTS_QUEUES + s.TAX_QUEUES

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
        """ Получить целевой месяц задачи. """

        return await super().get_target_month(issue, target_)
