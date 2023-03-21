from app.settings import log
from app.settings import settings as s
from app.utils import tracker_api
from ..utils import Tables


class BdrPlanTable(Tables):
    """ Утилиты таблицы БДР (План). """

    def __init__(self, year: int):
        """ Инициализация класса. """
        super().__init__()
        self.year = year

    async def get_data(self):
        """ Получить данные таблицы. """
        issues = await self.get_issues()

        data = {
            'incomes': {},
            'direct_contractors': {},
            'other_expenses': {},
            'management_company': {},
        }

        for issue in issues:
            queue = issue.queue.key
            stata_b = issue.stataBudzeta

            if queue in s.INCOMES_QUEUES:
                await self.distribute_data_by_articles(
                    issue,
                    data['incomes'],
                )

            elif queue in s.EXPENSES_QUEUES and 'Прямые подрядчики' in stata_b:
                await self.distribute_data_by_articles(
                    issue,
                    data['direct_contractors'],
                )

            elif queue in s.EXPENSES_QUEUES and 'Прочие расходы' in stata_b:
                await self.distribute_data_by_articles(
                    issue,
                    data['other_expenses'],
                )

            elif queue in s.EXPENSES_QUEUES and 'Услуги УК' in stata_b:
                await self.distribute_data_by_articles(
                    issue,
                    data['management_company'],
                )

        return data

    async def get_issues(self):
        """ Получить все нужные задачи. """
        all_issues = await tracker_api.get_list_issues()

        queues = s.INCOMES_QUEUES + s.EXPENSES_QUEUES + s.STAFF_SALARY_QUEUES

        filter_ = {
            'issue.queue.key': queues,
            'bool(issue.project.display)': True,
            'issue.summaEtapa != 0': True,
            'issue.end.split("-")[0]': str(self.year),
        }

        # Из общего списка задач фильтровать нужные
        issues = await self.get_target_issues(all_issues, filter_)

        if not issues:
            log.error('Задачи не были получены после фильтрации.')

        return issues

    async def distribute_data_by_articles(self, issue, data: dict) -> None:
        """
        Метод распределения данных из задачи по объекту словаря.
        Метод получает объект словаря и изменяет его, ничего не возвращая.
        """

        month = await self.get_target_month(issue)
        full_month = await self.convert_num_month_to_str_month(month)
        name = issue.summary
        summa_etapa = issue.summaEtapa

        if not summa_etapa:
            return

        if data_n := data.get(name):

            if data_n.get(full_month):
                data_n[full_month] += summa_etapa
                data_n['amount'] += summa_etapa

            else:
                data_n[full_month] = summa_etapa
                data_n['amount'] += summa_etapa

        else:
            data[name] = {full_month: summa_etapa, 'amount': summa_etapa}
