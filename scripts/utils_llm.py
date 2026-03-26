import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
api_key = os.getenv('GEMINI_API_KEY')
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    model = None

def translate_and_summarize(text, source_lang='auto'):
    """使用 Gemini API 進行翻譯和摘要"""
    if not model:
        return text # Fallback to original text if no API key
    
    prompt = f"""
    You are a professional game industry translator. 
    Please translate the following game art/outsourcing related title into Simplified Chinese (zh-CN).
    The translation should be natural and professional for the game industry.
    Format your response as a JSON object with 'translated_title' and 'summary' (a brief 1-sentence summary).
    
    Original Text: {text}
    """
    
    try:
        response = model.generate_content(prompt)
        import json
        import re
        
        # Extract JSON from response
        match = re.search(r'\{.*\}', response.text, re.DOTALL)
        if match:
            data = json.loads(match.group())
            return data.get('translated_title', text), data.get('summary', '')
    except Exception as e:
        print(f"Gemini translation failed: {e}")
    
    return text, ""
