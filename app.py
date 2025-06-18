from datetime import datetime
import gradio as gr

from agent.workflow import WorkFlow
from db.SQLiteDB import SQLiteDB
from log.logger import Logger

title = "健康食谱助手"
description = """🍲 <h1>健康食谱助手</h1>
<h3>您的智能私人营养师，为您量身打造健康饮食计划</h3>"""

submit_btn = '发送'
examples = [
    ["今天早餐吃了燕麦粥和牛奶", None], 
    ["午饭吃了西红柿炒鸡蛋和米饭", None], 
    ["这周我吃了哪些食物", None], 
    ["我应该补充什么营养", None]
]
style_options = ["轻松", "幽默", "正式"]

# CSS样式
custom_css = """
:root {
    --primary-color: #4CAF50;
    --secondary-color: #8BC34A;
    --text-color: #333;
    --light-bg: #f9f9f9;
    --card-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

#app-header {
    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
    color: white;
    padding: 20px;
    border-radius: 10px;
    margin-bottom: 20px;
    box-shadow: var(--card-shadow);
    text-align: center;
}

#app-header h1 {
    margin: 0;
    font-size: 32px;
}

#app-header h3 {
    margin: 10px 0 0;
    font-weight: normal;
    opacity: 0.9;
}

#sidebar {
    background-color: var(--light-bg);
    border-radius: 10px;
    padding: 20px;
    box-shadow: var(--card-shadow);
}

#sidebar .label {
    font-weight: bold;
    margin-bottom: 8px;
    color: var(--primary-color);
}

#chat-container {
    border-radius: 10px;
    box-shadow: var(--card-shadow);
    overflow: hidden;
}

#input-container {
    margin-top: 10px;
    border-radius: 10px;
    overflow: hidden;
}

#submit-btn {
    background-color: var(--primary-color);
    color: white;
}

#submit-btn:hover {
    background-color: var(--secondary-color);
}

#footer {
    text-align: center;
    margin-top: 30px;
    color: #777;
    font-size: 14px;
}

.examples-panel {
    margin-top: 20px;
    border-radius: 10px;
    overflow: hidden;
    box-shadow: var(--card-shadow);
}
"""

# 修改后的预测函数，加入用户输入的用户名参数
def predict(message, history, style, input_username):
    global user_name, sqLite
    user_name = input_username.strip()  # 去掉首尾空格

    if not user_name:
        # 如果用户名为空，提醒用户输入
        history = history or []
        history.append((message, "⚠️ 请先填写用户名再开始对话哦~"))
        return history, ""  # 返回历史记录和空字符串清空输入框
    
    # 检查用户是否存在，如果不存在则自动注册
    user_info = sqLite.get_user_by_name(user_name)
    is_new_user = False
    
    if not user_info:
        # 用户不存在，自动注册
        user_id = sqLite.register_user(user_name)
        is_new_user = True
        if user_id:
            print(f"已自动创建用户 {user_name}, ID: {user_id}")
        else:
            print(f"创建用户 {user_name} 失败")
            history = history or []
            history.append((message, "⚠️ 创建用户失败，请尝试使用其他用户名。"))
            return history, ""  # 返回历史记录和空字符串清空输入框
    
    dictionary = {'prompt': message}
    print(dictionary)

    if history is None:
        history = []
        
    # 如果是新用户且这是第一条消息，先显示欢迎信息
    if is_new_user and not history:
        welcome_msg = f"欢迎您，{user_name}！您的账号已自动创建成功。我是您的私人健康食谱助手，可以帮您记录每天的饮食，并提供健康饮食建议。"
        if style == "幽默":
            welcome_msg = "哎嘛~ " + welcome_msg + "吃得好才能活得好，让我来帮你打理好每一餐吧！"
        elif style == "正式":
            welcome_msg = "尊敬的用户，" + welcome_msg + "为您提供专业的健康饮食建议是我的荣幸。"
        else:
            welcome_msg = "嘿嘿~ " + welcome_msg + "开始记录您的健康饮食之旅吧！"
            
        history.append(("", welcome_msg))
        
        # 如果是欢迎消息，就直接返回，不进行后续处理
        if not message:
            return history, ""  # 返回历史记录和空字符串清空输入框

    history = history[-20:]
    model_input = []
    for chat in history:
        model_input.append({"role": "user", "content": chat[0]})
        model_input.append({"role": "assistant", "content": chat[1]})
    model_input.append({"role": "user", "content": message})
    print(model_input)

    try:
        user_name, response = workflow.run({"require": message, "user_name": user_name})
        print(response)

        if style == "幽默":
            response = "哎嘛~ " + response
        elif style == "正式":
            response = "尊敬的用户，" + response
        else:
            response = "嘿嘿~ " + response

        history.append((message, response))
        return history, ""  # 返回历史记录和空字符串清空输入框
    except Exception as e:
        print(f"workflow.run 方法执行出错: {e}")
        history.append((message, "很抱歉！宕机了！"))
        return history, ""  # 返回历史记录和空字符串清空输入框


# 构建 Gradio 页面
with gr.Blocks(title=title, theme=gr.themes.Soft(
    primary_hue="green",
    secondary_hue="green",
    neutral_hue="gray",
    radius_size=gr.themes.sizes.radius_sm,
    font=[gr.themes.GoogleFont("Noto Sans SC"), "ui-sans-serif", "system-ui", "sans-serif"],
)) as demo:
    # 应用自定义CSS
    gr.HTML(f"<style>{custom_css}</style>")
    
    # 页眉
    gr.HTML('<div id="app-header">🍲 <h1>健康食谱助手</h1><h3>您的智能私人营养师，为您量身打造健康饮食计划</h3></div>')
    
    with gr.Row():
        # 侧边栏
        with gr.Column(scale=1, elem_id="sidebar"):
            gr.HTML('<div class="label">👤 用户信息</div>')
            user_name_input = gr.Textbox(
                label="用户名", 
                placeholder="如：小明", 
                value="", 
                interactive=True,
                elem_id="username-input"
            )
            
            gr.HTML('<div class="label">🎭 对话风格</div>')
            style_dropdown = gr.Dropdown(
                choices=style_options, 
                value="轻松", 
                label="选择语气风格",
                elem_id="style-dropdown"
            )
            
            gr.HTML('<div class="label">📊 营养小贴士</div>')
            gr.HTML("""
            <ul>
                <li>每天应摄入300-500克蔬菜</li>
                <li>水果每天1-2份</li>
                <li>每周至少吃2-3次鱼类</li>
                <li>多饮水，每天1500-2000ml</li>
                <li>减少油盐糖的摄入</li>
            </ul>
            """)
            
        # 主聊天区域
        with gr.Column(scale=3):
            with gr.Box(elem_id="chat-container"):
                chatbot = gr.Chatbot(height=500, elem_id="chatbot")
                
                with gr.Row(elem_id="input-container"):
                    input_text = gr.Textbox(
                        placeholder="例如：今天早餐吃了什么、这周我吃了哪些食物、我应该补充什么营养...", 
                        show_label=False,
                        elem_id="input-text"
                    )
                    submit = gr.Button(submit_btn, elem_id="submit-btn")
            
            # 示例面板
            with gr.Accordion("💬 常用对话示例", open=True, elem_classes="examples-panel"):
                gr.Examples(
                    examples=examples, 
                    inputs=[input_text, style_dropdown],
                    label="点击尝试以下对话"
                )
    
    # 页脚
    gr.HTML('<div id="footer">© 2024 健康食谱助手 | 为您的健康保驾护航</div>')

    # 点击按钮或回车提交时调用 predict 函数，带上用户名输入
    submit.click(
        predict,
        inputs=[input_text, chatbot, style_dropdown, user_name_input],
        outputs=[chatbot, input_text],  # 添加input_text作为输出
        queue=True
    )
    input_text.submit(
        predict,
        inputs=[input_text, chatbot, style_dropdown, user_name_input],
        outputs=[chatbot, input_text],  # 添加input_text作为输出
        queue=True
    )

    # 确保在launch()之前启用队列
    demo.queue()


if __name__ == "__main__":
    sqLite = SQLiteDB("healthMealAssistant.db")
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    logger = Logger(f"test_{timestamp}_gty")
    user_name = ""  # 初始为空，由用户输入
    workflow = WorkFlow(sqLite, logger)
    demo.launch()