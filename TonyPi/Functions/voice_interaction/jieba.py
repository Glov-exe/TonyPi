import jieba
#import jieba.analyse
from collections import Counter

# 初始化jieba分词库
jieba.initialize()

# 自定义停用词列表（可根据需要扩展）
STOP_WORDS = set([
    '的', '了', '在', '是', '我', '有', '和', '就', 
    '不', '人', '都', '一', '一个', '也', '要', '这'
])

def tokenize(text):
    """分词处理函数"""
    # 使用jieba进行精确模式分词
    words = jieba.lcut(text)
    # 去除停用词和单字词
    filtered = [
        word for word in words 
        if len(word) > 1 
        and word not in STOP_WORDS 
        and not word.isspace()
    ]
    return filtered

def extract_keywords(text, top_n=10):
    """关键词提取函数"""
    # 基于TF-IDF算法提取关键词
    keywords = jieba.analyse.extract_tags(
        text, 
        topK=top_n, 
        withWeight=False,
        allowPOS=('n', 'vn', 'v')  # 允许的词性：名词、动名词、动词
    )
    return keywords

if __name__ == "__main__":
    # 获取用户输入
    user_input = input("请输入要分析的文本：\n")

    # 分词处理
    tokens = tokenize(user_input)
    print("\n分词结果：")
    print("/".join(tokens))

    # 词频统计
    word_counts = Counter(tokens)
    print("\n词频统计（前10）：")
    for word, count in word_counts.most_common(10):
        print(f"{word}: {count}")

    # 关键词提取
    keywords = extract_keywords(user_input)
    print("\n关键词提取：")
    print(", ".join(keywords))