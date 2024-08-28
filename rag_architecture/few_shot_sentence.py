from langchain_community.chat_models import ChatOpenAI
from langchain.prompts.few_shot import FewShotPromptTemplate
from langchain.prompts.prompt import PromptTemplate
from Examples.example import get_exapmle
from configs.load_config import LoadConfig
from langchain.chains import LLMChain
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import logging, os

example_fewshot = get_exapmle()

APP_CFG = LoadConfig()
llm = APP_CFG.load_openai_model()

def split_sentences(text_input, examples):
    example_formatter_template = """
        Input command from user: {input_text}
        The information extracted from above command:\n
        ----
        object: {object}
        price: {price}
        power: {power}
        weight: {weight}
        volume: {volume}
        specifications: {specifications}
    """

    example_prompt = PromptTemplate(
        input_variables=["input_text", "object", "price", "power", "weight", "volume", "specifications"],
        template=example_formatter_template,
    )

    few_shot_prompt = FewShotPromptTemplate(
        # These are the examples we want to insert into the prompt.
        examples=examples,
        # This is how we want to format the examples when we insert them into the prompt.
        example_prompt=example_prompt,
        # The prefix is some text that goes before the examples in the prompt.
        prefix="Extract detailed information for an input command asking. Return the corresponding object. Below are some examples:",
        # The suffix is some text that goes after the examples in the prompt.
        # Usually, this is where the user input will go
        suffix="Input command from user: {input_text}\nThe information extracted from above command:",
        # The input variables are the variables that the overall prompt expects.
        input_variables=["input_text"],
        # The example_separator is the string we will use to join the prefix, examples, and suffix together with.
        example_separator="\n\n",
    )

    # Print the formatted prompt for debugging purposes (optional)
    # print(few_shot_prompt.format(input_text="Mua den nang luong mat troi giá 15 triệu"))

    chain = few_shot_prompt | llm

    result = chain.invoke(input=text_input).content
    
    return result.lower()

def extract_info(sentences, examples):
    try:
        s = split_sentences(sentences, examples)
        variables = {}
        lines = s.strip().split('\n')
        for line in lines:
            parts = line.split(':')
            if len(parts) == 2:
                key = parts[0].strip()
                price = parts[1].strip()
                if key == 'object':
                    # Xử lý phần object
                    # Loại bỏ các dấu ngoặc và khoảng trắng
                    price = price.replace('[', '').replace(']', '').strip()
                    # Tách các giá trị theo dấu phẩy
                    object_list = [item.strip().strip("'") for item in price.split(',') if item.strip()]
                    variables[key] = object_list
                else:
                    variables[key] = price       
        return variables
    except Exception as e:
        s = {'object': sentences, 'power':'', 'prices':[''], 'weight': '','volume':'','specifications':''}
        print('extract object in few shot', s['object'])
        return s
    
def classify_intent(question):
    # Các specifications cần phân loại
    specificationss = ["giá", "công suất", "dung tích", "khối lượng", "số lượng","thông tin chung"]

    # Tạo prompt để phân loại câu hỏi
    prompt_template = """
    Phân loại câu hỏi sau đây chỉ một trong các loại sau: {specificationss}.

    Câu hỏi: {question}

    Loại:
    """
    prompt = PromptTemplate(
        input_variables=["specificationss", "question"],
            template=prompt_template,
    )

    # Tạo LLMChain để phân loại câu hỏi
    chain = prompt | llm

    # Hàm phân loại câu hỏi
    result = chain.invoke({
        "specificationss": ", ".join(specificationss),
        "question": question
    }).content
    # print("Result:", result)
    json_price = {}
    examples = []
    if "giá" in result.lower():
        examples = example_fewshot['parameter']['example_price']
        json_price =  extract_info(question, examples)
    elif "công suất" in result.lower():
        examples = example_fewshot['parameter']['example_power']
        json_price =  extract_info(question, examples)
    elif "khối lượng" in result.lower():
        examples = example_fewshot['parameter']['example_weight']
        json_price =  extract_info(question, examples)
    elif "dung tích" in result.lower():
        examples = example_fewshot['parameter']['example_volume']
        json_price =  extract_info(question, examples)
    else:
        examples = example_fewshot['parameter']['example_quantity']
        json_price =  extract_info(question, examples)

    return json_price

    # Ví dụ sử dụng
# question = "Tôi quan tâm tới sản phẩm đèn năng lượng mặt trời và Thiết bị Wifi có giá tiết kiệm"
# print(classify_specifications(question))   

def find_closest_match(input_str, list_product):
    match = process.extractOne(input_str, list_product, scorer=fuzz.partial_ratio)
    print(f"Có phải bạn tìm kiếm sản phẩm {match[0]}")
    print("Độ match:", match[1])
    # if match[1] >= 60:
    #     return match[0]
    # else:
    #     return 0
    return match
    
