import os
from groq import Groq
from typing import Optional

class GroqClient:
    def __init__(self, model: str = "llama-3.1-8b-instant"):
        self.model = model
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.language = "en"  # Default language

    def set_language(self, language: str):
        if language == "es":
            self.language = "es"
        else:
            self.language = "en"

    def system_prompt(self, topic, information) -> Optional[str]:
        return f"""You are a helpful local expert for Erasmus students in Salerno, Italy.
                    Your role is to provide practical, accurate information about {topic}
                    to help new international students navigate the city.

                    Available information:
                    {information}

                    Guidelines:
                    - Give clear, actionable advice based only on the information provided
                    - Be friendly and welcoming - remember these are new students who may feel overwhelmed
                    - If you cannot fully answer their question with the available information, politely direct them to contact ESN (Erasmus Student Network) volunteers for additional help
                    - Focus on practical details that will genuinely help students settle in
                    - Use a conversational but informative tone

                    Answer the student's question now."""
    
    def _get_info(self, topic: str):
        """
        Get information about a topic from the topics folder
        Args:
            topic: The topic to get information about
        Returns:
            Content of the topic file or empty string if not found
        """
        try:
            topic_file = f"llm/topics/{topic.lower()}.txt"
            with open(topic_file, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return ""
        except Exception:
            return ""


    def generate(self, prompt: str, topic: str , messages: Optional[list[str]]) -> str:
        """
        Generate a response from the Groq model
        Args:
            prompt: The user's prompt
            topic: the topic on which the student is asking the question
            messages: the previous messages in the chat (if there are)
            is_spanish: flag to check if the language is spanish
        Returns:
            Generated response from the model
        """

        sys_prompt = self.system_prompt(topic, self._get_info(topic))
        if self.language == "es":
            sys_prompt += " You must answer in Spanish."
        if messages:
            sys_prompt += str(messages)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1024
            )
            return response.choices[0].message.content

        except Exception as e:
            return f"Error connecting to Groq: {e}"

    

    def is_available(self) -> bool:
        """
        Check if Groq API is accessible

        Returns:
            True if Groq is available, False otherwise
        """
        try:
            # Test with a minimal request to check API availability
            test_response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1
            )
            return True
        except:
            return False