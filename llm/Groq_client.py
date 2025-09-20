import os
from groq import Groq
from typing import Optional
from rag.pipeline import RAGPipeline

class GroqClient:
    def __init__(self, model: str = "llama-3.1-8b-instant"):
        self.model = model
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.language = "en"  # Default language
        self.rag =  RAGPipeline("hyppo-data", "sentence-transformers/all-MiniLM-L6-v2", recreate_collection=False)

    def set_language(self, language: str):
        if language == "es":
            self.language = "es"
        else:
            self.language = "en"

    def system_prompt(self, information) -> Optional[str]:
        return f"""You are a helpful local expert for Erasmus students in Salerno, Italy.
                    Your role is to provide practical, accurate information to help new international students navigate the city.

                    Available information:
                    {information}

                    Guidelines:
                    - Give clear, actionable advice based ONLY on the information provided above
                    - Be friendly and welcoming - remember these are new students who may feel overwhelmed
                    - Keep responses concise (under 400 words) and avoid unnecessary details
                    - Focus on the current question - refer to previous messages only if directly relevant
                    - If you cannot fully answer with the available information, say: "I don't have that specific information, but ESN volunteers can help you with this"
                    - Focus on practical details that will genuinely help students settle in
                    - Use a conversational but informative tone
                    - Speak positively about Salerno and the ESN association

                    Answer the student's question directly:"""
                        
    def _get_info(self, user_prompt):
        """
        Activates rag pipeline to get info
        """
        return self.rag.search(user_prompt)
    
    def _turn_message_into_chat_format(self, messages: list[(str,str)]) -> list[dict]:
        chat = []
        for message in messages:
            chat.append({"role": "user", "content": message[0]})
            chat.append({"role": "system", "content": message[1]})
        return chat

    def generate(self, prompt: str, message_history: Optional[list[(str,str)]]) -> str:
        """
        Generate a response from the Groq model
        Args:
            prompt: The user's prompt
            message_history: the previous messages in the chat (if there are)
        Returns:
            Generated response from the model
        """

        sys_prompt = self.system_prompt(self._get_info(prompt))
        if self.language == "es":
            sys_prompt += " You must answer in Spanish."

        chat = [{"role": "system", "content": sys_prompt}]

        if message_history:
            chat.extend(self._turn_message_into_chat_format(message_history))

        chat.append({"role": "user", "content": prompt})
        print(chat)
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=chat,
                temperature=0.5,
                max_tokens=400
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