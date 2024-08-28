from langchain.memory import ConversationBufferWindowMemory
from source.retriever import get_context
from configs.load_config import LoadConfig
from source.utils.base_model import GradeReWrite, SeachingDecision
from source.utils.prompt import PROMPT_HISTORY, PROMPT_HEADER, PROMPT_ELS_OR_TEXT
from rag_architecture.few_shot_sentence import classify_intent
from rag_architecture.retrieval import search_db


APP_CFG = LoadConfig()
memory = ConversationBufferWindowMemory(memory_key="chat_history", k=3)

def get_history():
    history = memory.load_memory_variables({})
    return history['chat_history']


def rewrite_query(query: str, history: str) -> str: 
    """
    Arg:
        query: câu hỏi của người dùng
        history: lịch sử của người dùng
        Sử dụng LLM để viết lại câu hỏi của người dùng thành 1 câu mới.
    Return:
        trả về câu hỏi được viết lại.
    """
    llm_with_output = APP_CFG.load_rewrite_model().with_structured_output(GradeReWrite)
    query_rewrite = llm_with_output.invoke(PROMPT_HISTORY.format(question=query, chat_history=history)).rewrite
    return query_rewrite

def decision_search_type(query: str) -> str: 
    """
    Arg:
        query: câu hỏi của người dùng
        history: lịch sử của người dùng
        Sử dụng LLM để viết lại câu hỏi của người dùng thành 1 câu mới.
    Return:
        trả về câu hỏi được viết lại.
    """
    llm_with_output = APP_CFG.load_rewrite_model().with_structured_output(SeachingDecision)
    type = llm_with_output.invoke(PROMPT_ELS_OR_TEXT.format(query=query)).type
    return type

# def chat_with_history(query: str, history):
#     history_conversation = get_history()
#     query_rewrite = rewrite_query(query=query, history=history_conversation)
#     context = get_context(query=query_rewrite)
#     response = None

#     if context == "":

#         template = f'''
#         Hãy trò chuyện với khách hàng một cách thân thiện và tự nhiên. 
#         Trả lời các câu hỏi, chia sẻ thông tin hữu ích, và tham gia vào các cuộc trò chuyện đa dạng về nhiều chủ đề. 
#         Thích nghi với giọng điệu và phong cách của người dùng, đồng thời duy trì tính nhất quán và lịch sự.
#         Lưu ý: Khách hàng là người việt nên bạn chỉ được sử dụng tiếng việt

#         Question: {query}

#         Answer: '''

#         prompt = template.format(query=query)
#         response = APP_CFG.load_chatchit_model().invoke(prompt).content
        
#         memory.chat_memory.add_user_message(query)
#         memory.chat_memory.add_ai_message(response)
#         history.append((query, response))

#     else:
#         prompt_final = PROMPT_HEADER.format(question=query_rewrite, context=context)

#         response = llm.invoke(prompt_final).content

#         memory.chat_memory.add_user_message(query)
#         memory.chat_memory.add_ai_message(response)

#         history.append((query, response))

#     return "", history


def chat_with_history(query: str, history):
    print("-Start-")
    history_conversation = get_history()
    print(history_conversation)
    print("-" * 20)
    query_rewrite = rewrite_query(query=query, history=history_conversation)
    print(query_rewrite)
    print("-" * 30)
    
    type = decision_search_type(query_rewrite)
    print(type)
    if "ELS" in type:
        demands = classify_intent(query_rewrite)
        print("= = = = result few short = = = =:", demands)
        if len(demands['object']) >= 1:
            response_elastic, products, ok = search_db(demands)
            save_outtext = response_elastic
        else: 
            ok = 0
            save_outtext = "Anh/chị vui lòng cho em biết thêm thông tin để em có thể tư vấn chính xác hơn ạ!"
        prompt_final = PROMPT_HEADER.format(question=query_rewrite, context=save_outtext)
        
    else:
        context = get_context(query=query_rewrite)
        prompt_final = PROMPT_HEADER.format(question=query_rewrite, context=context)

    response = APP_CFG.load_rag_model().invoke(prompt_final).content
    print(response)
    print("-Finish-")
    
    memory.chat_memory.add_user_message(query)
    memory.chat_memory.add_ai_message(response)

    # Make sure 'history' is a list before appending
    if isinstance(history, list):
        history.append((query, response))

    return "", history


# response = chat_with_history(query="Tôi muốn mua điều hòa")
# print(response)