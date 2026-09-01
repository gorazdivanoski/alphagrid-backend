import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

def generate_real_ai_analysis(stock_data: dict) -> dict:
    try:
        # Го користиме Gemini 1.5 Flash - извонредно брз модел за структурирани податоци
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config={"response_mime_type": "application/json"}
        )

        prompt = f"""
            Ти си експерт за финансиски пазари и Senior Quant Analyst.
            Направи длабока, структурирана анализа за следната компанија врз основа на достапните реални податоци:

            - Симбол: {stock_data.get('ticker')}
            - Сектор: {stock_data.get('sector')}
            - Тековна цена: ${stock_data.get('current_price')} {stock_data.get('currency')}
            - Индикатори:
                * RSI (14 дена): {stock_data.get('indicators', {}).get('rsi_14')}
                * SMA 50 дена: ${stock_data.get('indicators', {}).get('sma_50')}
                * SMA 200 дена: ${stock_data.get('indicators', {}).get('sma_200')}
            - Сленден Earnings датум: {stock_data.get('next_earnings_date')}
            - Бизнис профил: {stock_data.get('business_summary')}

            Напиши анализа исклучиво на македонски јазик во следниот JSON формат:
            {{
                "executive_summary": "Синтетизирано фундаментално резиме за бизнисот и неговата моментална позиција.",
                "technical_analysis": "Објаснување на RSI и подвижните просеци (SMA 50/200) и што значат за моментумот.",
                "risk_factors": "Кои се клучните ризици што инвеститорот треба да ги земе предвид.",
                "ai_verdict": "Јасен финални заклучок (Bullish, Bearish или Neutral) со аргументација."
            }}
            """
        response = model.generate_content(prompt)
        parsed_response = json.loads(response.text)

        return {
            "ticker": stock_data.get('ticker'),
            "model_used": "Gemini 1.5 Flash",
            "analysis": parsed_response
        }
    except Exception as e:
        return {"error": f"Грешка при генерирање на AI анализа: {str(e)}"}