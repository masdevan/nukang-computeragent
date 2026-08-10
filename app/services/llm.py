class ChatAgent:
    def __init__(self, base_url, api_key, model):
        self.base_url = base_url
        self.api_key = api_key
        self.model = model

    def build_client(self):
        import openai

        return openai.OpenAI(base_url=self.base_url, api_key=self.api_key)
