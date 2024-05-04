
from openai import OpenAI

client = OpenAI(api_key='sk-proj-uXTeK3jF5LhLCHdgKaEAT3BlbkFJbmmhYydyWf53EnLlMMM1')
msgs = []
msgs.append({"role": "user", "content": "Produce a short summary of this conversation."})

response = client.chat.completions.create(
                model='gpt-4-turbo',
                messages=msgs,
            )
response = response.choices[0].message.content
print(response)