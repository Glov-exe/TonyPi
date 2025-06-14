import re
from collections import OrderedDict

class KeywordExtractor:
    def __init__(self, keyword_dict=None, dict_path=None):
        """
        初始化关键词提取器
        :param keyword_dict: 直接传入的关键词集合
        :param dict_path: 关键词词典文件路径
        """
        self.keywords = set()
        
        # 加载关键词词典
        if keyword_dict:
            self.keywords.update(keyword_dict)
        if dict_path:
            self._load_dict(dict_path)
            
        # 构建匹配模式（按词长降序排列，确保优先匹配长词）
        sorted_keywords = sorted(self.keywords, key=len, reverse=True)
        self.pattern = re.compile("|".join(map(re.escape, sorted_keywords)))
        
        # 停用词列表（可扩展）
        self.stop_words = {"然后", "接着", "之后", "再", "请", "的", "了", "吧"}
    
    def _load_dict(self, path):
        """从文件加载关键词词典"""
        try:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        self.keywords.add(line)
            print(f"词典加载成功，共加载 {len(self.keywords)} 个关键词")
        except Exception as e:
            print(f"词典加载失败: {str(e)}")
    
    def extract(self, text, remove_stopwords=True, keep_order=True):
        """
        从文本提取关键词
        :param text: 输入文本
        :param remove_stopwords: 是否过滤停用词
        :param keep_order: 是否保持原始出现顺序
        :return: 提取到的关键词列表
        """
        # 全匹配查找关键词
        matches = self.pattern.findall(text)
        
        # 过滤停用词
        if remove_stopwords:
            matches = [word for word in matches if word not in self.stop_words]
        
        # 去重并保持顺序
        if keep_order:
            return list(OrderedDict.fromkeys(matches))
        return list(set(matches))

# 使用示例
if __name__ == "__main__":
    # 初始化提取器（从词典文件加载）
    extractor = KeywordExtractor(dict_path="Functions/learn/audio/files/dict.txt")  # 假设关键词词典文件名为keywords.txt
    
    # 测试语句
    test_sentences = [
        "请先前进然后左转，最后挥手示意",
        "检测颜色之后停止识别，再做两个俯卧撑",
        "先鞠躬然后跳舞庆祝一下",
        "向后转然后前进三步"
    ]
    
    for sentence in test_sentences:
        keywords = extractor.extract(sentence)
        print(f"原句: {sentence}")
        print(f"提取结果: {keywords}")
        print("-" * 50)