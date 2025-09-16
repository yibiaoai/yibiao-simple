

def read_expand_outline_prompt():
  '''从简版技术方案中提取目录的提示词'''
  system_prompt = """你是一个专业的标书编写专家。需要从用户提交的标书技术方案中，提取出目录结构。

  要求：
  1. 目录结构要全面覆盖技术标的所有必要目录，包含多级目录
  2. 如果技术方案中有章节名称，则直接使用技术方案中的章节名称
  3. 如果技术方案中没有章节名称，则结合全文，总结出章节名称
  5. 返回标准JSON格式，包含章节编号、标题、描述和子章节，注意编号要连贯
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
  return system_prompt
  
def generate_outline_prompt(overview, requirements):
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
  return system_prompt, user_prompt


  
def generate_outline_with_old_prompt(overview, requirements, old_outline):
  system_prompt = """你是一个专业的标书编写专家。根据提供的项目概述和技术评分要求，生成投标文件中技术标部分的目录结构。
  用户会提供一个自己编写的目录，你要保证目录满足技术评分要求，并充分结合用户自己编写的目录。
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
  用户自己编写的目录：
  {old_outline}

  项目概述：
  {overview}

  技术评分要求：
  {requirements}

  请生成完整的技术标目录结构，确保覆盖所有技术评分要点。"""
  return system_prompt, user_prompt