import ollama
from typing import Optional

class OllamaClient:
    def __init__(self, model: str = "llama2", system_prompt: Optional[str] = None):
        self.model = model
        self._system_prompt = system_prompt
        self.client = ollama.Client()

    @property
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
        return ""


    def generate(self, prompt: str, topic: str , messages: Optional[list[str]], is_spanish: bool =False) -> str:
        """
        Generate a response from the Ollama model
        Args:
            prompt: The user's prompt
            topic: the topic on which the student is asking the question
            messages: the previous messages in the chat (if there are)
            is_spanish: flag to check if the language is spanish
        Returns:
            Generated response from the model
        """
        
        sys_prompt = self.system_prompt(topic)
        if is_spanish:
            sys_prompt += " You must answer in Spanish."
        if messages:
            sys_prompt = self.system_prompt + messages

        try:
            response = self.client.generate(
                model=self.model,
                prompt=prompt,
                system=sys_prompt,
                stream=False
            )
            return response['response']

        except Exception as e:
            return f"Error connecting to Ollama: {e}"

    

    def is_available(self) -> bool:
        """
        Check if Ollama is running and accessible

        Returns:
            True if Ollama is available, False otherwise
        """
        try:
            self.client.list()
            return True
        except:
            return False