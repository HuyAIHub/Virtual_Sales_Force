import gradio as gr
from configs.load_config import LoadConfig
from source.chat import chat_with_history
APP_CFG = LoadConfig()

def reset_conversation():
    # Thêm tin nhắn chào hỏi vào đây
    return [("", "Xin chào! 😊 Em là Bot VCC, trợ lý mua săm tại VCC sẵn sàng tư vấn cho anh/chị về các sản phẩm bên em. Rất vui được hỗ trợ anh/chị hôm nay! Chúc anh/chị một ngày tuyệt vời! 😊")], []


with gr.Blocks(css="""
    #chatbot { 
        height: 100%; 
        overflow-y: auto; 
        border: 1px solid #ddd; 
        border-radius: 15px; 
        padding: 20px;
        background-color: #f7f7f7;
    }
    #chatbot .user, #chatbot .bot { 
        padding: 10px 15px; 
        border-radius: 20px; 
        display: inline-block;
    }
    #chatbot .user { 
        background-color: #FF1493; 
        color: black;
        float: right;
    }
    #chatbot .bot { 
        background-color: #F0F8FF; 
        color: black;
        float: left;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    #chat-header {
        text-align: center;
        padding: 20px;
        background-color: #FF1493;
        color: white;
        border-radius: 15px 15px 0 0;
        margin-bottom: 20px;
    }
    #msg-box {
        border-radius: 20px;
        border: 1px solid #ddd;
    }
    #send-btn, #reset-btn, #clear-btn {
        border-radius: 20px;
    }
    .button-row {
        display: flex;
        justify-content: space-between;
        margin-top: 10px;
    }
""") as demo:
    gr.HTML("""
    <div id="chat-header">
        <h1 style="color: #000000">💬 Chat với AI Assistant</h1>
        <p style="color: #000000">Hãy đặt câu hỏi, tôi sẽ cố gắng trả lời bạn!</p>
    </div>
    """)

    
    
    chatbot = gr.Chatbot(
        [("", "Xin chào! 😊 Em là Bot VCC, trợ lý mua săm tại VCC sẵn sàng tư vấn cho anh/chị về các sản phẩm bên em. Rất vui được hỗ trợ anh/chị hôm nay! Chúc anh/chị một ngày tuyệt vời! 😊")],
        elem_id="chatbot",
        bubble_full_width=False,
        avatar_images=("images/avt_vcc.png", "images/avt_bot.png"),
    )
    
    with gr.Row():
        txt = gr.Textbox(
            show_label=False,
            placeholder="Nhập tin nhắn của bạn ở đây...",
            elem_id="msg-box"
        )
        submit_btn = gr.Button("Gửi", elem_id="send-btn")


    txt.submit(chat_with_history, [txt, chatbot], [txt, chatbot])
    submit_btn.click(chat_with_history, [txt, chatbot], [txt, chatbot])

    with gr.Row(elem_classes="button-row"):
        clear = gr.Button("Xóa tin nhắn", elem_id="clear-btn")
        reset = gr.Button("Reset cuộc trò chuyện", elem_id="reset-btn")

    clear.click(lambda: None, None, chatbot, queue=False)
    reset.click(reset_conversation, outputs=[chatbot, txt])

# import numpy as np
# import gradio as gr

# def sepia(input_img, strength):
#     sepia_filter = strength * np.array(
#         [[0.393, 0.769, 0.189], [0.349, 0.686, 0.168], [0.272, 0.534, 0.131]]
#     ) + (1-strength) * np.identity(3)
#     sepia_img = input_img.dot(sepia_filter.T)
#     sepia_img /= sepia_img.max()
#     return sepia_img

# callback = gr.CSVLogger()

# with gr.Blocks() as demo:
#     with gr.Row():
#         with gr.Column():
#             img_input = gr.Image()
#             strength = gr.Slider(0, 1, 0.5)
#         img_output = gr.Image()
#     with gr.Row():
#         btn = gr.Button("Flag")

#     # This needs to be called at some point prior to the first call to callback.flag()
#     callback.setup([img_input, strength, img_output], "flagged_data_points")

#     img_input.change(sepia, [img_input, strength], img_output)
#     strength.change(sepia, [img_input, strength], img_output)

#     # We can choose which components to flag -- in this case, we'll flag all of them
#     btn.click(lambda *args: callback.flag(list(args)), [img_input, strength, img_output], None, preprocess=False)

demo.launch(share = True)


