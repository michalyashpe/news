from openai import OpenAI
import logging
import os
from ..config.settings import OPENROUTER_BASE_URL, OPENROUTER_API_KEY

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        logger.info(f"Checking OPENROUTER_API_KEY: {'*' * len(OPENROUTER_API_KEY) if OPENROUTER_API_KEY else 'None'}")
        logger.info(f"Environment variables: {os.environ.get('OPENROUTER_API_KEY')}")
        
        if not OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY environment variable is not set")
            
        self.client = OpenAI(
            base_url=OPENROUTER_BASE_URL,
            api_key=OPENROUTER_API_KEY
        )

    def is_new_information(self, new_headline, recent_headlines):
        """Check if a headline contains new information compared to recent headlines"""
        try:
            content = f"""You are a news reporter.
            You need to answer in YES or NO. No other word is allowed.
            Is the following headline new information? {new_headline} 
            
            Here are the recent headlines: {recent_headlines}"""
            
            messages = [{"role": "user", "content": content}]
            
            completion = self.client.chat.completions.create(
                model="deepseek/deepseek-r1-zero:free",
                messages=messages
            )
            
            response = completion.choices[0].message.content.strip().upper()
            return response == "YES"
        except Exception as e:
            logger.error(f"Error in LLM service: {str(e)}")
            return False 