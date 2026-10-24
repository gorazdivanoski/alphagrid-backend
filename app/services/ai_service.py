# AI service for generating stock analyses and answering follow-up questions,
# using Google Gemini and real-time market data.

from google import genai
from app.core.config import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY)

def get_stock_analysis(ticker: str, quote_data: dict) -> str:
    prompt = f"""Ти си финансиски аналитичар кој пишува кратки stock briefing-и за инвеститори.

Компанија: {quote_data['name']} ({ticker})
Моментална цена: ${quote_data['price']}
Дневна промена: {quote_data['percent_change']}%
Волумен: {quote_data.get('volume', 'N/A')}

Напиши анализа во ТОЧНО оваа структура, на македонски јазик:

1. Прв пасус (2-3 реченици): Кратко опиши со што точно се занимава {quote_data['name']} - нивниот основен бизнис, индустрија, и клучни производи/услуги. Користи го твоето знаење за компанијата.

2. Втор пасус (2-3 реченици): Објасни ја моменталната техничка слика - цената, промената, волуменот, и што тоа значи за краткорочниот моментум. Не давaj buy/sell/hold препораки.

Вкупно максимум 6 реченици. Не додавaj наслови/bullet points, само двата пасуси еден по друг."""

    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
        )
        return response.text
    except Exception as e:
        return f"AI анализата моментално не е достапна ({str(e)})"

def get_followup_answer(ticker: str, quote_data: dict, question: str, previous_analysis: str | None = None) -> str:
    context = f"""Ти си финансиски аналитичар кој разговара со инвеститор за акцијата {quote_data['name']} ({ticker}).

Тековни податоци:
Цена: ${quote_data['price']}
Дневна промена: {quote_data['percent_change']}%
Волумен: {quote_data.get('volume', 'N/A')}
"""

    if previous_analysis:
        context += f"\nПретходна анализа што веќе ја имаш дадено:\n{previous_analysis}\n"

    context += f"""
Инвеститорот сега прашува: "{question}"

Одговори кратко и јасно (максимум 4-5 реченици), на македонски јазик. Не давaj buy/sell/hold финансиски совети - само објективни информации и контекст. Ако прашањето бара податок што го немаш (пр. точни финансиски извештаи, идни настани надвор од твоето знаење), кажи тоа искрено наместо да измислуваш бројки."""

    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=context,
        )
        return response.text
    except Exception as e:
        return f"Не успеав да дадам одговор ({str(e)})"