import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get('DASHSCOPE_API_KEY'),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)


def generate_test_cases(feature, count=10):
    """为指定功能生成测试用例，输出 YAML 格式"""
    prompt = f"""请为「{feature}」设计 {count} 条测试用例。

    严格按照以下 YAML 格式输出，不要加任何解释文字、不要用 Markdown 代码块包裹：

    - case_id: TC_001
      title: 用例标题
      precondition: 前置条件
      steps: 操作步骤
      expected: 预期结果
    - case_id: TC_002
      title: 用例标题
      precondition: 前置条件
      steps: 操作步骤
      expected: 预期结果
    """
    response = client.chat.completions.create(
        model="qwen-plus",
        messages=[
            {"role": "system", "content": "你是一个资深的软件测试工程师，擅长设计测试用例。"},
            {"role": "user",
             "content": prompt}
        ],
        stream=False
    )
    return response.choices[0].message.content


# 测试一下
if __name__ == "__main__":
    feature = input("请输入要测试的功能：")  # 比如输入"登录功能"
    result = generate_test_cases(feature)
    print(result)

    # 保存到yaml文件
    with open(f"data/ai_case.yaml", "w", encoding="utf-8") as f:
        f.write(result)
    print(f"\n已保存到 data/ai_case.yaml,审核后可复制到data/test_data.yaml")