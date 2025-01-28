import sys
from openai import OpenAI

api_key_file = 'ai_teach_api_key.txt'

with open(api_key_file, 'r') as f:
    api_key = f.readline().strip()
if api_key == '':
    print(f'please input correct api key in{api_key_file}')
    sys.exit()

client = OpenAI(api_key=api_key)

# completion = client.chat.completions.create(
#     # model="gpt-4o",
#     model="o1-preview",
#     messages=[
#         {"role": "developer", "content": "You are a helpful assistant. 請用繁體中文回答"},
#         {
#             "role": "user",
#             "content": [
#                 {"type": "text", "text": "這張影像是什麼?"},
#                 {
#                     "type": "image_url",
#                     "image_url": {
#                         "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg",
#                     },
#                 },
#             ],
#         }
#     ],
#     frequency_penalty=0.0,
#     max_completion_tokens=15000,
#     n=1,
#     presence_penalty=0.0,
#     temperature=1.0,
#     top_p=1.0,
# )

completion = client.chat.completions.create(
  # model="o1-preview",
  model='o1-preview',
  messages=[
    {"role": "user", "content": "你是 gpt-4 還是 o1? 請解數學題目, 題目是: 一個三位數abc，能被9整除；交換a與c的位置，所的數cba能被5整除，求滿足條件的最小三位數?"},
  ]
)

print(completion.choices[0].message)

# print(completion)
print(completion.choices[0].message.content)