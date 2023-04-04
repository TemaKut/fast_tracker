from isodate import parse_duration

from app.settings import log


class Tables:
    """ Класс низкоуровневых операций с таблицами. """
    def __init__(self, year: int):
        """ Инициализация класса. """
        self.year = year
        self.work_hours_per_month = {
            "january": 136,
            "february": 144,
            "march": 176,
            "april": 160,
            "may": 160,
            "june": 168,
            "july": 168,
            "august": 184,
            "september": 168,
            "october": 176,
            "november": 168,
            "december": 168,
        }
        self.decoded_months = {
            '01': 'january',
            '02': 'february',
            '03': 'march',
            '04': 'april',
            '05': 'may',
            '06': 'june',
            '07': 'july',
            '08': 'august',
            '09': 'september',
            '10': 'october',
            '11': 'november',
            '12': 'december',
        }

    async def distribute_data(self, issue, full_month, data, key) -> None:
        """
        Метод распределения данных из задачи по объекту словаря.
        Метод получает объект словаря и изменяет его, ничего не возвращая.
        """
        name = issue.summary
        summa_etapa = issue.summaEtapa

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

        # Распределение доходов перед налогооблажением (общей суммы)
        if i_bt := data.get('incomes_before_tax'):

            if i_bt.get(full_month):
                i_bt[full_month] += summa_etapa
                i_bt['amount'] += summa_etapa

            else:
                i_bt[full_month] = summa_etapa
                i_bt['amount'] += summa_etapa

        else:
            data['incomes_before_tax'] = {
                full_month: summa_etapa,
                'amount': summa_etapa,
            }

    async def get_target_issues(self, issues: list, filter_: dict) -> list:
        """
        Получить целевые задачи из списка.
        filter_ должен содержать в себе ключ,
        равноситьный обращению к объекту issue
        Пример: filter_ = {'issue.assignee.display': 'Andrey Nikitin'}
        """
        if not isinstance(issues, list) or not isinstance(filter_, dict):
            log.error('Неверные параметры. issues -> [], filter_ -> dict')
            raise ValueError('Неверные параметры. issues or filter_')

        data = []

        for issue in issues:
            count_validated_items = 0
            have_to_be_validated_items = len(filter_)

            for key, value in filter_.items():

                try:

                    if isinstance(value, list):

                        if eval(key) in value:
                            count_validated_items += 1

                    elif eval(key) == value:
                        count_validated_items += 1

                except Exception:
                    continue

            if count_validated_items == have_to_be_validated_items:
                data.append(issue)
        return data

    async def is_start_and_end_within_one_month(self, issue) -> Exception:
        """ Проверка находится ли задача в рамках одного месяца. """
        start = issue.start.split("-")[1]
        end = issue.end.split("-")[1]

        if start != end:
            raise ValueError('Задача не в рамках одного месяца.')

    async def duration_to_work_hours(self, duration: str) -> int:
        """ Преобразование промежутка времени в рабочие часы. """
        if not isinstance(duration, str | None):
            log.critical('Переменная duration не str.')
            raise ValueError('duration должно быть строкой.')

        duration = parse_duration(duration)

        hours = duration.seconds // 3600
        weekends = (duration.days // 7) * 2
        week_days = duration.days - weekends
        work_hours = (week_days * 8) + hours

        return work_hours

    async def get_target_month(self, issue, target_: str = 'end'):
        """ Получить целевой месяц задачи. """
        if target_ not in ['end', 'deadline']:
            log.error('target_ -> in ["end", "deadline"]')
            raise ValueError('target_ -> in ["end", "deadline"]')

        if target_ == 'end':
            return issue.end.split("-")[1]

        return issue.deadline.split("-")[1]

    async def convert_num_month_to_str_month(self, num_month: str) -> str:
        """ Конвертировать числовое обозначение месяца в полное строчное """
        if num_month not in self.decoded_months:
            log.error('Месяц передан неправильно.')
            raise ValueError('Месяц передан неправильно.')

        return self.decoded_months[num_month]

    async def is_issue_in_target_year(self, issue, year, target_: str = 'end'):
        """ Возбудить исключение если задача не в рамках учётного года. """
        if target_ not in ['end', 'deadline']:
            log.error('target_ -> in ["end", "deadline"]')
            raise ValueError('target_ -> in ["end", "deadline"]')

        if target_ == 'end':
            start_year = issue.start.split("-")[0]
            end_year = issue.end.split("-")[0]

            if (start_year != str(year)) or (end_year != str(year)):

                raise ValueError()

        else:
            start_year = issue.start.split("-")[0]
            deadline_year = issue.deadline.split("-")[0]

            if (start_year != str(year)) or (deadline_year != str(year)):

                raise ValueError()

    async def is_issue_end_in_year(self, issue, year, target_: str = 'end'):
        """ Возбудить исключение если задача не в рамках учётного года. """
        if target_ not in ['end', 'deadline']:
            log.error('target_ -> in ["end", "deadline"]')
            raise ValueError('target_ -> in ["end", "deadline"]')

        if target_ == 'end':
            end_year = issue.end.split("-")[0]

            if end_year != str(year):

                raise ValueError()

        else:
            deadline_year = issue.deadline.split("-")[0]

            if deadline_year != str(year):

                raise ValueError()
