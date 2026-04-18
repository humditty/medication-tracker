"""Google Translate 免费 API 实现

使用 Google Translate 的免费接口进行翻译。
无需 API Key，但可能有速率限制。
"""
import urllib.parse
import urllib.request
import json
from .translator import BaseTranslator, TranslationResult


class GoogleTranslator(BaseTranslator):
    """Google Translate 免费 API 实现
    
    使用 translate.googleapis.com 的免费接口。
    优点：无需 API Key，完全免费
    缺点：可能有速率限制，不适合大规模使用
    """
    
    @property
    def name(self) -> str:
        return "Google Translate"
    
    def translate(
        self,
        text: str,
        target_lang: str = "zh-CN",
        source_lang: str = "auto"
    ) -> TranslationResult:
        """执行翻译
        
        Args:
            text: 要翻译的文本
            target_lang: 目标语言代码
            source_lang: 源语言代码（默认 auto）
        
        Returns:
            TranslationResult 对象
        """
        if not text or not text.strip():
            return TranslationResult(
                success=False,
                original_text=text,
                error_message="文本为空",
                engine_name=self.name
            )
        
        base_url = "https://translate.googleapis.com/translate_a/single"
        
        params = {
            "client": "gtx",
            "sl": source_lang,
            "tl": target_lang,
            "dt": "t",
            "q": text
        }
        
        url = f"{base_url}?{urllib.parse.urlencode(params)}"
        
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                
                if data and data[0]:
                    result = "".join(
                        part[0] for part in data[0] if part[0]
                    )
                    return TranslationResult(
                        success=True,
                        original_text=text,
                        translated_text=result,
                        engine_name=self.name
                    )
                else:
                    return TranslationResult(
                        success=False,
                        original_text=text,
                        error_message="API 返回空结果",
                        engine_name=self.name
                    )
        except urllib.error.URLError as e:
            return TranslationResult(
                success=False,
                original_text=text,
                error_message=f"网络请求失败: {str(e)[:50]}",
                engine_name=self.name
            )
        except Exception as e:
            return TranslationResult(
                success=False,
                original_text=text,
                error_message=f"翻译异常: {str(e)[:50]}",
                engine_name=self.name
            )
    
    def is_available(self) -> bool:
        """检查服务是否可用
        
        Google 免费 API 无需 API Key，始终可用。
        
        Returns:
            True
        """
        return True
