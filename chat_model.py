import openai
from record_audio import Record_to_audio
from text_to_voice import Text_to_voice
import tkinter as tk
from threading import Thread

with open('my_api_key.txt', 'r') as f:
    api_key = f.readline().strip()
if api_key == '':
    print('please input correct api key in my_api_key.txt')
    exit()

# Define OpenAI API key 
openai.api_key = api_key

# Set up the model and prompt
c = input('1. gpt-3.5-turbo\n2. code-davinci-002\n')
if c != '1' and c != '2':
    print('ERROR!! please input correct number!')
    exit()

print()

text_or_voice = input('1. text in text out\n2. text in voice out\n3. voice in text out\n4. voice in voice out\n')
if text_or_voice != '1' and text_or_voice != '2' and text_or_voice != '3' and text_or_voice != '4':
    print('ERROR!! please input correct number!')
    exit()

# gpt-3.5-turbo
# code-davinci-002

my_record = Record_to_audio()
my_text_to_voice = Text_to_voice()

def button_trigger():
    global my_button
    if my_record.star_flag:
        my_record.star_flag = False
        my_button.config(text='開始聆聽')
    else:
        my_record.star_flag = True
        my_button.config(text='停止')

def close_tk():
    global root
    my_record.stop_program = True
    root.destroy()

root = tk.Tk()
root.protocol("WM_DELETE_WINDOW", close_tk)
my_button = tk.Button(root, text='開始聆聽', font=('微軟正黑體', 20, 'bold'), width=20, command=button_trigger)
my_button['state'] = tk.DISABLED
my_button.pack()

def my_thread():
    if c == '1':
        model_engine = "gpt-3.5-turbo"
        messages = [
            # system message first, it helps set the behavior of the assistant
            {"role": "system", "content": "You are a helpful assistant."},
        ]
        while True:
            if text_or_voice == '1':
                message = input("我: ")
                if message != '':
                    messages.append(
                        {"role": "user", "content": message},
                    )
                    chat_completion = openai.ChatCompletion.create(
                        model=model_engine, messages=messages
                    )
                elif message == 'stop' or message == '停止':
                    break
                else:
                    continue
                reply = chat_completion.choices[0].message.content
                print(f"AI: {reply}\n")
                messages.append({"role": "assistant", "content": reply})
            elif text_or_voice == '4':
                # temp = input('press any key to start listen')
                my_button['state'] = tk.NORMAL
                f = my_record.start_recording()
                if my_record.stop_program == True:
                    break
                my_button['state'] = tk.DISABLED
                transcript = openai.Audio.transcribe("whisper-1", f, language='zh')
                message = transcript['text']
                print(f'我: {message}')
                # message = input("我: ")
                if message == 'stop' or message == '停止':
                    break
                elif  message != '':
                    messages.append(
                        {"role": "user", "content": message},
                    )
                    chat_completion = openai.ChatCompletion.create(
                        model=model_engine, messages=messages
                    )
                else:
                    continue
                reply = chat_completion.choices[0].message.content
                print(f"AI: {reply}\n")
                my_text_to_voice.play_voice(reply, speed_up=1.5)
                messages.append({"role": "assistant", "content": reply})
    elif c == '2':
        model_engine = "code-davinci-002"
        #with open('my_text.txt', 'r', encoding='UTF-8') as f:
        #    prompt = f.read()

        prompt = "# Python 3 \n# Calculate the mean distance between an array of points"

        # Generate a response
        completion = openai.Completion.create(
            engine=model_engine,
            prompt=prompt,
            max_tokens=8000,
            n=1,
            stop=None,
            temperature=0.5,          # What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic.
        )

        response = completion.choices[0].text
        print(response)

t1 = Thread(target=my_thread)
t1.start()

root.mainloop()
# root.destroy()
t1.join()
print('finish')