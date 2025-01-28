from openai import OpenAI
import base64
import os
import sys
import threading
import subprocess
import tempfile

api_key_file = 'ai_teach_api_key.txt'

with open(api_key_file, 'r') as f:
    api_key = f.readline().strip()
if api_key == '':
    print(f'please input correct api key in{api_key_file}')
    sys.exit()

client = OpenAI(api_key=api_key)

# target_dir = 'input_tmp'
target_dir = 'input'
cou = 0
thread_lock = threading.Lock()

def encode_image(image_path:str):
    try:
        if image_path.endswith('.png') or image_path.endswith('.PNG'):
            from PIL import Image
            with Image.open(image_path) as img:
                # Convert to RGB if has alpha channel
                if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                    bg = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode != 'RGBA':
                        img = img.convert('RGBA')
                    bg.paste(img, mask=img.split()[3])
                    img = bg
                # Convert to bytes directly
                from io import BytesIO
                buffer = BytesIO()
                img.save(buffer, format='PNG')
                return base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        # For non-PNG files, read directly
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
            
    except Exception as e:
        raise Exception(f"Failed to encode image {image_path}: {str(e)}")

def openai_thread(input_txt:str, total_dir_len:int, sub_dir:str, img_file_name:str):
    global cou
    # completion = client.chat.completions.create(
    #     model="gpt-4o",
    #     messages=[
    #         {"role": "system", "content": "請用繁體中文回答。你是一位數學解題老師，請透過step by step的方式解出題目的答案。在每一步都反覆迭代，確認邏輯沒有問題，最終輸出一個完整解答。"},
    #         {
    #             "role": "user",
    #             "content": [
    #                 {
    #                     "type": "text",
    #                     "text": input_txt,
    #                 },
    #             ],
    #         }
    #     ],
    #     frequency_penalty=0.0,
    #     max_completion_tokens=15000,
    #     n=1,
    #     presence_penalty=0.0,
    #     temperature=0.7,
    #     top_p=1.0,
    # )

    add_prompt = f'這是一個數學問題，請用繁體中文回答。你是一位數學解題老師，請透過step by step的方式解出題目的答案。在每一步都反覆迭代，確認邏輯沒有問題，最終輸出一個完整解答。\n題目如下:\n{input_txt}'

    completion = client.chat.completions.create(
        model="o1-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": add_prompt,
                    },
                ],
            },
        ],
        frequency_penalty=0.0,
        max_completion_tokens=15000,
        n=1,
        presence_penalty=0.0,
        temperature=1.0,
        top_p=1.0,
    )

    # print(completion.choices[0].message.content)

    md_to_docx(completion.choices[0].message.content, f'{sub_dir}/output.docx')
    with thread_lock:
        cou += 1
        # 每個 thread 印出目前的 cou 數以及總共的 dir 數
        print(f'{cou}/{total_dir_len}', end='\r')

def md_to_docx(md_content: str, output_path: str):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".md", mode="w", encoding="utf-8") as temp_md:
        temp_md_name = temp_md.name
        temp_md.write(md_content)
    
    try:
        # 在這裡加上 -f markdown+raw_tex+tex_math_single_backslash
        # 或者 --include-in-header
        subprocess.run(
            [
                "pandoc",
                "-s",
                "-f", "markdown+raw_tex+tex_math_single_backslash",
                temp_md_name,
                "-o", output_path
            ],
            check=True
        )
    finally:
        if os.path.exists(temp_md_name):
            os.remove(temp_md_name)


def main():
    all_dir_list = os.listdir(target_dir)
    total_dir_len = len(all_dir_list)
    print(f'{cou}/{total_dir_len}', end='\r')
    for dir_name in all_dir_list:
        # image_files = []
        # img_encodings = []
        for f in os.listdir(f'{target_dir}/{dir_name}') :
            if f.endswith('.txt'):
                with open(f'{target_dir}/{dir_name}/{f}', 'r', encoding='utf-8') as txt_file:
                    input_txt = txt_file.read()
                threading.Thread(target=openai_thread, args=(input_txt, total_dir_len, f'{target_dir}/{dir_name}', f)).start()
                # openai_thread(base64_image, f'{target_dir}/{dir_name}', f)


if __name__ == '__main__':
    main()