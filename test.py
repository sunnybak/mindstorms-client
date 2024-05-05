from openai import OpenAI

client = OpenAI(api_key='sk-proj-Gxa6OeFmoePlz04nf33sdofsjkFJ00amYaRJhwF7gE0pVLve')
msgs = []
msgs.append({"role": "user", "content": "Produce a short summary of this conversation."})

response = client.chat.completions.create(
                model='gpt-4-turbo',
                messages=msgs,
            )
response = response.choices[0].message.content
print(response)