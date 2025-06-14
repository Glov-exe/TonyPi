class BiMaxMatchSegmenter:

    def __init__(self, word_dict=None, dict_path=None):
        """
        初始化分词器
        :param word_dict: 可直接传入词典集合
        :param dict_path: 或传入词典文件路径
        """
        if word_dict is None:
            word_dict = set()
        
        # 如果提供了词典路径，从文件加载
        if dict_path:
            try:
                with open(dict_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            word_dict.add(line)
                print(f"成功加载词典，共 {len(word_dict)} 个词条")  # 调试信息
            except Exception as e:
                print(f"加载词典失败: {str(e)}")
                print(f"尝试加载的路径: {dict_path}")
        
        self.word_dict = word_dict
        self.max_word_len = max(len(word) for word in word_dict) if word_dict else 0
        print(f"最大词长: {self.max_word_len}")  # 调试信息
    
    def forward_max_match(self, text):
        """正向最大匹配算法"""
        if not text:
            return []
        
        start = 0
        n = len(text)
        result = []
        
        while start < n:
            end = min(start + self.max_word_len, n)
            word = None
            
            # 从最大长度开始尝试匹配
            for l in range(end - start, 0, -1):
                candidate = text[start:start+l]
                if candidate in self.word_dict:
                    word = candidate
                    break
            
            if word is None:  # 未匹配到词典中的词，按单字切分
                word = text[start]
                start += 1
            else:
                start += len(word)
            
            result.append(word)
        
        return result
    
    def backward_max_match(self, text):
        """反向最大匹配算法"""
        if not text:
            return []
        
        end = len(text)
        result = []
        
        while end > 0:
            start = max(0, end - self.max_word_len)
            word = None
            
            # 从最大长度开始尝试匹配
            for l in range(end - start, 0, -1):
                candidate = text[start:start+l]
                if candidate in self.word_dict:
                    word = candidate
                    break
            
            if word is None:  # 未匹配到词典中的词，按单字切分
                word = text[end-1]
                end -= 1
            else:
                end -= len(word)
            
            result.insert(0, word)  # 反向插入
        
        return result
    
    def segment(self, text):
        """双向最大匹配分词"""
        if not text:
            return []
        
        # 获取两种分词结果
        fmm_result = self.forward_max_match(text)
        bmm_result = self.backward_max_match(text)
        
        # 选择更优的分词结果
        if len(fmm_result) == len(bmm_result):
            # 分词数量相同，选择单字较少的分词结果
            fmm_single = sum(1 for w in fmm_result if len(w) == 1)
            bmm_single = sum(1 for w in bmm_result if len(w) == 1)
            return fmm_result if fmm_single <= bmm_single else bmm_result
        else:
            # 选择分词数量较少的结果
            return fmm_result if len(fmm_result) < len(bmm_result) else bmm_result


# 使用示例
if __name__ == "__main__":
    # 正确使用方式：明确指定参数名
    dict_path = "/home/pi/TonyPi/Functions/learn/audio/files/dict.txt"
    segmenter = BiMaxMatchSegmenter(dict_path=dict_path)  # 关键修改：指定参数名
    
    # 打印加载的词典内容（调试用）
    print("加载的词典样例:", list(segmenter.word_dict)[:10])  # 显示前10个词
    
    test_cases = [
        "北京大学",
        "清华大学研究生",
        "北京大学生命科学院",
        "研究生命科学",
        "前进鞠躬"
    ]
    
    for text in test_cases:
        print(f"原文: {text}")
        print(f"正向最大匹配: {segmenter.forward_max_match(text)}")
        print(f"反向最大匹配: {segmenter.backward_max_match(text)}")
        print(f"双向最大匹配: {segmenter.segment(text)}")
        print("-" * 50)