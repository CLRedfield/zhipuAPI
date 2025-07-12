import os
from zhipuai import ZhipuAI

def main():
    # 从环境变量中获取API密钥，或者直接在代码中指定
    # 建议使用环境变量以提高安全性
    api_key = os.getenv("ZHIPUAI_API_KEY", "133e608f967247f285c297bdeeaed081.CXhxRhwuxtmafx78")
    if not api_key:
        print("错误：未设置 ZHIPUAI_API_KEY 环境变量，也未在代码中指定。")
        print("请在终端中运行 export ZHIPUAI_API_KEY='your_api_key' 或直接在代码中修改。")
        return

    try:
        client = ZhipuAI(api_key=api_key)
    except Exception as e:
        print(f"初始化客户端时出错: {e}")
        return

    # 保存对话历史
    conversation_history = []

    print("您好！我是 GLM-4 Flash。我们现在可以开始对话了。")
    print("输入 'exit', 'quit' 或 '再见' 来结束对话。")
    print("-" * 20)

    while True:
        try:
            user_input = input("您: ")
            if user_input.lower() in ["exit", "quit", "再见"]:
                print("AI: 感谢您的使用，再见！")
                break
            
            # 将用户输入添加到对话历史
            conversation_history.append({"role": "user", "content": user_input})

            # 调用API
            response = client.chat.completions.create(
                model="glm-4-flash-250414",
                messages=conversation_history,
                stream=True,  # 设置为True以接收流式回复
            )

            # 处理流式输出
            model_response = ""
            print("AI: ", end="")
            try:
                for chunk in response:
                    content = chunk.choices[0].delta.content
                    if content is not None:
                        print(content, end="", flush=True)
                        model_response += content
            finally:
                print() # 确保在回复结束后换行

            if model_response:
                # 将模型的完整回复也添加到对话历史
                conversation_history.append({"role": "assistant", "content": model_response})
            else:
                # 如果没有收到有效回复，移除刚才的用户输入
                conversation_history.pop()
                print("AI: 抱歉，我没有收到有效的回复。")


        except (KeyboardInterrupt):
            print("\nAI: 感谢您的使用，再见！")
            break
        except Exception as e:
            print(f"发生错误: {e}")
            # 如果发生错误，可以选择性地移除最后一次的用户输入，避免影响后续对话
            if conversation_history and conversation_history[-1]['role'] == 'user':
                 conversation_history.pop()


if __name__ == "__main__":
    main() 