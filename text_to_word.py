import subprocess
import tempfile
import os

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

if __name__ == "__main__":
    # 測試的 Markdown 字串
    example_md = """

# 測試 Markdown + LaTeX (from Python)
這是一個行內公式：\( E = mc^2 \)

這是一個分行公式：
\[
\frac{\partial \Psi}{\partial t} = \hat{H}\Psi
\]

# 化學方程式示例 (Markdown + LaTeX)

這是一個行內公式示例：$2 H_2 + O_2 \to 2 H_2O$

這是一個分行公式示例：
$$
\mathrm{C_6H_6} + \frac{15}{2}\mathrm{O_2} \;\longrightarrow\; 6 \mathrm{CO_2} + 3 \mathrm{H_2O}
$$

再舉一個分行公式：
$$
2 \mathrm{KClO_3} \;\longrightarrow\; 2 \mathrm{KCl} + 3 \mathrm{O_2}
$$

"""

    # 輸出 docx 檔案
    md_to_docx(example_md, "output.docx")
    print("轉檔完成，請打開 output.docx 查看效果。")
