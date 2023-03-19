from fastapi import APIRouter
from ..source_tracker_api.utils import tracker_api


tables_router = APIRouter()


@tables_router.get('/bdr/plan/incomes')
async def bdr_plan_incomes():
    """ БДР (План)/ Доходы """
    issues = await tracker_api.get_list_issues()

    data = {}
    for issue in issues:

        if issue.queue.key == 'FINVYRUCKA':
            summary = issue.summary
            end = issue.end.split('-')[1]
            summa_etapa = issue.summaEtapa

            if data_summary := data.get(summary):

                if data_summary_end := data_summary.get(end):
                    data_summary[data_summary_end] += summa_etapa

                else:
                    data_summary[end] = summa_etapa

            else:
                data[summary] = {end: summa_etapa}

    return data
