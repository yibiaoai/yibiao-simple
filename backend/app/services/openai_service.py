"""OpenAI服务"""
import openai
from typing import Generator, Dict, Any, List
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor


class OpenAIService:
    """OpenAI服务类"""
    
    def __init__(self, api_key: str, base_url: str = None, model_name: str = "gpt-3.5-turbo"):
        """初始化OpenAI服务"""
        self.api_key = api_key
        self.base_url = base_url
        self.model_name = model_name
        
        # 初始化OpenAI客户端
        self.client = openai.OpenAI(
            api_key=api_key,
            base_url=base_url if base_url else None
        )
    
    async def get_available_models(self) -> List[str]:
        """获取可用的模型列表"""
        try:
            def _get_models():
                models = self.client.models.list()
                chat_models = []
                for model in models.data:
                    model_id = model.id.lower()
                    if any(keyword in model_id for keyword in ['gpt', 'claude', 'chat', 'llama', 'qwen', 'deepseek']):
                        chat_models.append(model.id)
                return sorted(list(set(chat_models)))
            
            # 在线程池中执行同步操作
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                models = await loop.run_in_executor(executor, _get_models)
            
            return models
        except Exception as e:
            raise Exception(f"获取模型列表失败: {str(e)}")
    
    async def stream_chat_completion(
        self, 
        messages: list, 
        temperature: float = 0.7,
        response_format: dict = None
    ) -> Generator[str, None, None]:
        """流式聊天完成请求"""
        def _stream():
            try:
                stream = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=temperature,
                    stream=True,
                    **({"response_format": response_format} if response_format is not None else {})
                )
                
                for chunk in stream:
                    if chunk.choices[0].delta.content is not None:
                        yield chunk.choices[0].delta.content
                        
            except Exception as e:
                yield f"错误: {str(e)}"
        
        # 在线程池中执行流式操作
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            future = executor.submit(lambda: list(_stream()))
            result = await loop.run_in_executor(None, lambda: future.result())
            
            for chunk in result:
                yield chunk
    
    async def analyze_document(self, file_content: str, analysis_type: str = "overview") -> str:
        """分析文档内容"""
        if analysis_type == "overview":
            system_prompt = """你是一个专业的招标文件分析专家。请分析上传的招标文件，提取并总结项目概述信息。
            
请重点关注以下方面：
1. 项目名称和基本信息
2. 项目背景和目的
3. 项目规模和预算
4. 项目时间安排
5. 主要技术特点
6. 关键要求

工作要求：
1. 保持提取信息的全面性和准确性，尽量使用原文内容，不要自己编写
2. 只关注与项目实施有关的内容，不提取商务信息
3. 直接返回整理好的项目概述，除此之外不返回任何其他内容
"""
        else:  # requirements
            system_prompt = """你是一个专业的招标文件分析专家。请分析上传的招标文件，提取技术评分要求,为编写投标文件中的技术方案做准备。
            
请重点关注以下方面：
1. 理解技术评分的意思：用于编写、评比投标文件中技术标的标准，关注技术方案、实施计划、技术能力、质量控制、创新性等内容，避免混淆商务评分（资质、信誉、合同条款）和价格评分（报价金额）
2. 仅提取技术评分项及相关要求，不包括商务、价格及其他
3. 生成内容要确保是从招标文件中提取的，不要自己编写
4. 直接返回整理好的技术评分要求，除此之外不返回任何其他内容
"""
        
        analysis_type_cn = "项目概述" if analysis_type == "overview" else "技术评分要求"
        user_prompt = f"请分析以下招标文件内容，提取{analysis_type_cn}信息：\n\n{file_content}"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # 收集所有流式响应
        full_content = ""
        async for chunk in self.stream_chat_completion(messages, temperature=0.3):
            full_content += chunk
        
        return full_content.strip()
    
    async def generate_outline(self, overview: str, requirements: str) -> Dict[str, Any]:
        """生成标书目录结构"""
        system_prompt = """你是一个专业的标书编写专家。根据提供的项目概述和技术评分要求，生成投标文件中技术标部分的目录结构。

要求：
1. 目录结构要全面覆盖技术标的所有必要章节
2. 章节名称要专业、准确，符合投标文件规范
3. 一级目录名称要与技术评分要求中的章节名称一致，如果技术评分要求中没有章节名称，则结合技术评分要求中的内容，生成一级目录名称
4. 一共包括三级目录
5. 返回标准JSON格式，包含章节编号、标题、描述和子章节
6. 除了JSON结果外，不要输出任何其他内容

JSON格式要求：
{
  "outline": [
    {
      "id": "1",
      "title": "",
      "description": "",
      "children": [
        {
          "id": "1.1",
          "title": "",
          "description": "",
          "children":[
              {
                "id": "1.1.1",
                "title": "",
                "description": ""
              }
          ]
        }
      ]
    }
  ]
}
"""
        
        user_prompt = f"""请基于以下项目信息生成标书目录结构：

项目概述：
{overview}

技术评分要求：
{requirements}

请生成完整的技术标目录结构，确保覆盖所有技术评分要点。"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # 收集所有流式响应
        full_content = ""
        async for chunk in self.stream_chat_completion(messages, temperature=0.7, response_format={"type": "json_object"}):
            full_content += chunk
        
        try:
            return json.loads(full_content.strip())
        except json.JSONDecodeError:
            raise Exception("生成的目录格式不正确")
    
    async def generate_content_for_outline(self, outline: Dict[str, Any], project_overview: str = "") -> Dict[str, Any]:
        """为目录结构生成内容"""
        try:
            if not isinstance(outline, dict) or 'outline' not in outline:
                raise Exception("无效的outline数据格式")
            
            # 深拷贝outline数据
            import copy
            result_outline = copy.deepcopy(outline)
            
            # 递归处理目录
            await self._process_outline_recursive(result_outline['outline'], [], project_overview)
            
            return result_outline
            
        except Exception as e:
            raise Exception(f"处理过程中发生错误: {str(e)}")
    
    async def _process_outline_recursive(self, chapters: list, parent_chapters: list = None, project_overview: str = ""):
        """递归处理章节列表"""
        for chapter in chapters:
            chapter_id = chapter.get('id', 'unknown')
            chapter_title = chapter.get('title', '未命名章节')
            
            # 检查是否为叶子节点
            is_leaf = 'children' not in chapter or not chapter.get('children', [])
            
            # 准备当前章节信息
            current_chapter_info = {
                'id': chapter_id,
                'title': chapter_title,
                'description': chapter.get('description', '')
            }
            
            # 构建完整的上级章节列表
            current_parent_chapters = []
            if parent_chapters:
                current_parent_chapters.extend(parent_chapters)
            current_parent_chapters.append(current_chapter_info)
            
            if is_leaf:
                # 为叶子节点生成内容
                content = await self._generate_chapter_content(chapter, current_parent_chapters[:-1], project_overview)
                if content:
                    chapter['content'] = content
            else:
                # 递归处理子章节
                await self._process_outline_recursive(chapter['children'], current_parent_chapters, project_overview)
    
    async def _generate_chapter_content(self, chapter: dict, parent_chapters: list = None, project_overview: str = "") -> str:
        """为单个章节生成内容"""
        try:
            chapter_id = chapter.get('id', 'unknown')
            chapter_title = chapter.get('title', '未命名章节')
            chapter_description = chapter.get('description', '')
            
            # 构建提示词
            system_prompt = """你是一个专业的标书编写专家，负责为投标文件的技术标部分生成具体内容。

要求：
1. 内容要专业、准确，与章节标题和描述保持一致
2. 这是技术方案，不是宣传报告，注意朴实无华，不要假大空
3. 语言要正式、规范，符合标书写作要求，但不要使用奇怪的连接词，不要让人觉得内容像是AI生成的
4. 内容要详细具体，避免空泛的描述
5. 直接返回章节内容，不生成标题，不要任何额外说明或格式标记
"""
            
            # 构建上下文信息
            context_info = ""
            
            # 上级章节信息
            if parent_chapters:
                context_info += "上级章节信息：\n"
                for parent in parent_chapters:
                    context_info += f"- {parent['id']} {parent['title']}\n  {parent['description']}\n"
            
            # 构建用户提示词
            project_info = ""
            if project_overview.strip():
                project_info = f"项目概述信息：\n{project_overview}\n\n"
            
            user_prompt = f"""请为以下标书章节生成具体内容：

{project_info}{context_info if context_info else ''}当前章节信息：
章节ID: {chapter_id}
章节标题: {chapter_title}
章节描述: {chapter_description}

请根据项目概述信息和上述章节层级关系，生成详细的专业内容，确保与上级章节的内容逻辑相承。"""
            
            # 调用AI生成内容
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            # 收集所有生成的文本
            full_content = ""
            async for chunk in self.stream_chat_completion(messages, temperature=0.7):
                full_content += chunk
            
            return full_content.strip()
            
        except Exception as e:
            print(f"生成章节内容时出错: {str(e)}")
            return ""