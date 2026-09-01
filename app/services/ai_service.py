import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

def generate_real_ai_analysis(stock_data: dict) -> dict:
    if not api_key:
        return {"error": "GEMINI_API_KEY не е пронајден во .env фајлот."}

    try:
        # Го користиме потврдениот модел gemini-2.5-flash од твојата достапна листа
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            generation_config={"response_mime_type": "application/json"}
        )

        prompt = f"""
        Ти си експерт за финансиски пазари и Senior Quant Analyst.
        Направи длабока, структурирана анализа за следната компанија:

        - Симбол: {stock_data.get('ticker')}
        - Сектор: {stock_data.get('sector')}
        - Тековна цена: ${stock_data.get('current_price')} {stock_data.get('currency')}
        - Индикатори:
            * RSI (14): {stock_data.get('indicators', {}).get('rsi_14')}
            * SMA 50: ${stock_data.get('indicators', {}).get('sma_50')}
            * SMA 200: ${stock_data.get('indicators', {}).get('sma_200')}
        - Следен Earnings датум: {stock_data.get('next_earnings_date')}
        - Бизнис профил: {stock_data.get('business_summary')}

        Врати анализа исклучиво на македонски јазик во следниот JSON формат:
        {{
            "executive_summary": "Синтетизирано фундаментално резиме за бизнисот.",
            "technical_analysis": "Објаснување на RSI и подвижните просеци (SMA 50/200).",
            "risk_factors": "Клучни ризици за инвеститорот.",
            "ai_verdict": "Јасен финални заклучок (Bullish, Bearish или Neutral) со аргументација."
        }}
        """

        response = model.generate_content(prompt)
        return {
            "ticker": stock_data.get("ticker"),
            "model_used": "gemini-2.5-flash",
            "analysis": json.loads(response.text)
        }
    except Exception as e:
        return {"error": f"Грешка со Gemini API: {str(e)}"}