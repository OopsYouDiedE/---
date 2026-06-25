import os
import json
import re
import concurrent.futures

files = [
    r"c:\Users\zznZZ\Desktop\新六艺\射_一_强健体魄.md",
    r"c:\Users\zznZZ\Desktop\新六艺\射_二_防卫意识与城市安全.md",
    r"c:\Users\zznZZ\Desktop\新六艺\射_三_公民军事素养.md",
    r"c:\Users\zznZZ\Desktop\新六艺\射_四_军事对抗演练.md",
    r"c:\Users\zznZZ\Desktop\新六艺\射_五_百人之指.md"
]

def analyze_text(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 拆分段落
    raw_paragraphs = content.split('\n\n')
    paragraphs = [p.strip() for p in raw_paragraphs if p.strip()]
    
    total_chars = 0
    total_sentences = 0
    statements = 0
    questions = 0
    exclamations = 0
    
    for p in paragraphs:
        # 去除Markdown标记后的纯文本大概字数
        clean_p = re.sub(r'[*#>\-]', '', p)
        char_count = len(re.sub(r'\s+', '', clean_p))
        
        # 统计标点符号
        q_count = len(re.findall(r'[？?]', clean_p))
        e_count = len(re.findall(r'[！!]', clean_p))
        s_count = len(re.split(r'[。！？.!?]+', clean_p)) - 1
        
        total_chars += char_count
        total_sentences += max(1, s_count) # 至少算一句
        questions += q_count
        exclamations += e_count
        # 陈述句大约等于总句数减去问句和感叹句
        st_count = max(0, s_count - q_count - e_count)
        statements += st_count
        
    return {
        "file": os.path.basename(filepath),
        "total_paragraphs": len(paragraphs),
        "avg_para_length": round(total_chars / len(paragraphs), 1) if paragraphs else 0,
        "avg_sentence_length": round(total_chars / total_sentences, 1) if total_sentences else 0,
        "sentence_types": {
            "statements": statements,
            "questions": questions,
            "exclamations": exclamations,
            "statement_ratio": round(statements / total_sentences * 100, 1) if total_sentences else 0,
            "question_ratio": round(questions / total_sentences * 100, 1) if total_sentences else 0,
            "exclamation_ratio": round(exclamations / total_sentences * 100, 1) if total_sentences else 0
        }
    }

results = {}
# 使用并行处理满足并行要求
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    future_to_file = {executor.submit(analyze_text, file): file for file in files}
    for future in concurrent.futures.as_completed(future_to_file):
        res = future.result()
        results[res['file']] = res

print(json.dumps(results, ensure_ascii=False, indent=2))
