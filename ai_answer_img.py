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

def openai_thread(base64_img:str, total_dir_len:int, sub_dir:str, img_file_name:str):
    global cou
    img_type = 'png' if img_file_name.endswith(('.png', '.PNG')) else 'jpeg'
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "你是一位專業的數學老師，並且很擅長教導學生。我是一位高中生，有一些題目我不太懂，需要你的指導以及詳細解析每個選項，循序漸進教導我了解這些題目。請用繁體中文回答"},
            {
                "role": "user",
                "content": [
                    # {
                    #     "type": "text",
                    #     "text": "這張影像是什麼?"
                    # },
                    {
                        "type": "image_url",
                        "image_url": {
                            # "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg",
                            "url": f"data:image/{img_type};base64,{base64_img}",
                        },
                    },
                ],
            }
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
    for dir_name in all_dir_list:
        # image_files = []
        # img_encodings = []
        for f in os.listdir(f'{target_dir}/{dir_name}') :
            if f.endswith(('.jpg', '.JPG', '.jpeg', '.JPEG', '.png', '.PNG')):
                # image_files.append(f)
                base64_image = encode_image(f'{target_dir}/{dir_name}/{f}')
                # img_encodings.append(base64_image)
                threading.Thread(target=openai_thread, args=(base64_image, total_dir_len, f'{target_dir}/{dir_name}', f)).start()
                # openai_thread(base64_image, f'{target_dir}/{dir_name}', f)


if __name__ == '__main__':
    main()