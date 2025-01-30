from openai import OpenAI
import base64
import os
import sys
import threading
import subprocess
import tempfile
import shutil
import concurrent.futures

class AI_Answer:
    def __init__(self):
        self.api_key_file = 'ai_teach_api_key.txt'
        self.padoc_path = 'pandoc-3.6.2'
        self.output_file_name = 'output.docx'
        self.max_thread_num = 7
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=self.max_thread_num)
        self.all_tasks_done = threading.Event()
        # target_dir = 'input_tmp'
        self.target_dir = 'input'
        self.cou = 0
        self.thread_lock = threading.Lock()

        with open(self.api_key_file, 'r') as f:
            api_key = f.readline().strip()
        if api_key == '':
            print(f'please input correct api key in {self.api_key_file}')
            sys.exit()

        self.client = OpenAI(api_key=api_key)

    def encode_image(self, image_path:str):
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

    def openai_img_thread(self, base64_img:str, sub_dir:str, img_file_name:str):
        # global cou
        img_type = 'png' if img_file_name.endswith(('.png', '.PNG')) else 'jpeg'
        completion = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "這是一個數學問題，請用繁體中文回答。你是一位數學解題老師，請透過step by step的方式解出題目的答案。在每一步都反覆迭代，確認邏輯沒有問題，最終輸出一個完整解答。\n題目如下:\n"},
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
        print('---------------------------------')
        print(f'model: {completion.model}')
        print('---------------------------------')
        print(f'usage: {completion.usage}')

        self.md_to_docx(completion.choices[0].message.content, f'{sub_dir}/{self.output_file_name}')

    def openai_txt_thread(self, input_txt:str, sub_dir:str):
        add_prompt = f'這是一個數學問題，請用繁體中文回答。你是一位數學解題老師，請透過step by step的方式解出題目的答案。在每一步都反覆迭代，確認邏輯沒有問題，最終輸出一個完整解答。\n題目如下:\n{input_txt}'

        completion = self.client.chat.completions.create(
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
        print('---------------------------------')
        print(f'model: {completion.model}')
        print('---------------------------------')
        print(f'usage: {completion.usage}')

        self.md_to_docx(completion.choices[0].message.content, f'{sub_dir}/{self.output_file_name}')

    def md_to_docx(self, md_content: str, output_path: str):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".md", mode="w", encoding="utf-8") as temp_md:
            temp_md_name = temp_md.name
            temp_md.write(md_content)
        
        try:
            # 在這裡加上 -f markdown+raw_tex+tex_math_single_backslash
            # 或者 --include-in-header
            subprocess.run(
                [
                    f'{self.padoc_path}/pandoc.exe',
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

    def background_result_logger(self, futures:list):
        """ 背景執行緒：當任務完成時立即輸出結果 """
        for f in concurrent.futures.as_completed(futures):
            result = f.result()
            # print(f"[Background] Task result: {result}")
            with self.thread_lock:
                self.cou += 1
                # 每個 thread 印出目前的 cou 數以及總共的 dir 數
                print(f'{self.cou}/{self.total_dir_len}', end='\r')

        # 當所有 futures 完成後，設置 Event
        self.all_tasks_done.set()

    def check_legal_file_architecture(self, name_list:list):
        for dir_name in name_list:
            if not os.path.isdir(f'{self.target_dir}/{dir_name}'):
                print(f'在 {self.target_dir} 資料夾內的 {dir_name} 不是資料夾')
                return False
        return True

    def gen_answer_to_word_file(self):
        if os.path.isdir(self.target_dir) == False:
            print(f'找不到 {self.target_dir} 資料夾')
            return None
        name_list = os.listdir(self.target_dir)
        if not self.check_legal_file_architecture(name_list):
            return None
        self.total_dir_len = len(name_list)
        print(f'{self.cou}/{self.total_dir_len}', end='\r')

        futures:list = []

        for dir_name in name_list:
            # image_files = []
            # img_encodings = []
            if os.path.exists(f'{self.target_dir}/{dir_name}/{self.output_file_name}'):
                os.remove(f'{self.target_dir}/{dir_name}/{self.output_file_name}')
            for f in os.listdir(f'{self.target_dir}/{dir_name}') :
                if f.endswith(('.jpg', '.JPG', '.jpeg', '.JPEG', '.png', '.PNG')):
                    # image_files.append(f)
                    base64_image = self.encode_image(f'{self.target_dir}/{dir_name}/{f}')
                    # img_encodings.append(base64_image)
                    # openai_img_thread(base64_image, f'{target_dir}/{dir_name}', f)
                    # t = threading.Thread(target=self.openai_img_thread, args=(base64_image, f'{self.target_dir}/{dir_name}', f), daemon=True)
                    # t.start()
                    f = self.executor.submit(self.openai_img_thread, base64_image, f'{self.target_dir}/{dir_name}', f)
                    futures.append(f)
                elif f.endswith('.txt'):
                    with open(f'{self.target_dir}/{dir_name}/{f}', 'r', encoding='utf-8') as txt_file:
                        input_txt = txt_file.read()
                    f = self.executor.submit(self.openai_txt_thread, input_txt, f'{self.target_dir}/{dir_name}')
                    futures.append(f)

        logging_thread = threading.Thread(target=self.background_result_logger, args=(futures,), daemon=True)
        logging_thread.start()

        self.all_tasks_done.wait()
        print("\nAll tasks are completed!")
        self.executor.shutdown(wait=False)

if __name__ == '__main__':
    a = AI_Answer()
    a.gen_answer_to_word_file()
