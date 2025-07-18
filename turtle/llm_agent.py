
try:
    # load environment variables from .env file (requires `python-dotenv`)
    from dotenv import load_dotenv
    load_dotenv(dotenv_path="./.env", override=True)
except ImportError:
    pass

from datetime import datetime
from datetime import timedelta
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from langchain.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage

import baostock as bs
import pandas as pd



@tool
def search_stock_data(code: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    获取指定股票在指定时间段内的历史K线数据。

    Args:
        code (str): 股票代码。
        start_date (str): 查询开始日期，格式为YYYY-MM-DD。
        end_date (str): 查询结束日期，格式为YYYY-MM-DD。

    Returns:
        pd.DataFrame: 包含股票历史K线数据的DataFrame，包含日期、开盘价、最高价、最低价、收盘价、成交量、成交额和复权因子等列。

    Raises:
        Exception: 如果查询出错，抛出异常，异常信息为错误信息。
    """
    # 豆包fuction call时结束时间需要矫正
    end_date = datetime.today().strftime('%Y-%m-%d') 
    bs.login()
    rs = bs.query_history_k_data_plus(code,
        "date,code,open,high,low,close,volume,amount,adjustflag",
        start_date=start_date,
        end_date=end_date,
        frequency="d",
        adjustflag="3")

    if rs.error_code != "0":
        print("error code: ", rs.error_code)
        bs.logout()
        raise Exception(rs.error_msg)

    # 获取具体的信息
    result_list = []
    while (rs.error_code == '0') & rs.next():
        # 分页查询，将每页信息合并在一起
        result_list.append(rs.get_row_data())
    result = pd.DataFrame(result_list, columns=rs.fields)
    # print(result)
    result['date'] = pd.to_datetime(result['date'])
    result['open'] = pd.to_numeric(result['open'])
    result['high'] = pd.to_numeric(result['high'])
    result['low'] = pd.to_numeric(result['low'])
    result['close'] = pd.to_numeric(result['close'])
    result['volume'] = pd.to_numeric(result['volume'])
    result['amount'] = pd.to_numeric(result['amount'])
    bs.logout()
    return result


# Create the agent
# model = init_chat_model("ernie-4.0-8k-latest", model_provider="openai")
# model = init_chat_model("doubao-seed-1-6-250615", model_provider="openai")
model = init_chat_model("doubao-seed-1-6-flash-250615", model_provider="openai")
agent = create_react_agent(
    model,
    [search_stock_data],
    checkpointer=MemorySaver()
)

def get_name(code: str) -> str:
    import pandas as pd
    df = pd.read_csv('data/hs300_stocks.csv')
    row = df[df['code'] == code]
    if not row.empty:
        return row['code_name']
    df = pd.read_csv('data/zz500_stocks.csv')
    row = df[df['code'] == code]
    if not row.empty:
        return row['code_name']
    return ''


def ask_llm(code):
    today = datetime.today()
    end_date = today.strftime('%Y-%m-%d')
    start_date = today - timedelta(days=360)
    config = {"configurable": {"thread_id": "abc123"}}
    input_messages = [
        SystemMessage(f"你是桥水基金创始人, 瑞·达利欧。根据用户输入从{start_date}到{end_date}股票数据，sma和macd数据，结合交易量和当前K线趋势，预测未来股价走势"),
        HumanMessage(f"股票code: {code}. 名称: {get_name(code)}"),
    ]
    
    msg = '' 

    for step in agent.stream(
        {"messages": input_messages}, config, stream_mode="values"
    ):
        # 这里先不拼接，function call的内容也会在stream中返回, 我只要最终结果
        msg = step["messages"][-1].content
    return msg

if __name__ == "__main__":
    import os
    # load environment variables from .env file (requires `python-dotenv`)
    from dotenv import load_dotenv
    load_dotenv(dotenv_path="./.env", override=True)

    sender = str(os.environ.get("EMAIL_SENDER"))
    receiver = str(os.environ.get("EMAIL_RECEIVER"))
    passwd = str(os.environ.get("EMAIL_PASSWD"))

    import markdown
    import notification

    # content = ask_llm('sz.000858')
    # content = markdown.markdown(content)
    # print(content)
    # notification.send_email_smtp(
    #     subject="五粮液今日分析",
    #     body=content,
    #     to_emails=[receiver],
    #     auth_code=passwd,
    # )

    # content = ask_llm('sz.000887')
    # content = markdown.markdown(content)
    # print(content)
    # notification.send_email_smtp(
    #     subject="中鼎股份日分析",
    #     body=content,
    #     to_emails=[receiver],
    #     auth_code=passwd,
    # )

    print("===================美亚光电===============")
    content = ask_llm('sz.002690') 
    content = markdown.markdown(content)
    notification.send_email_smtp(
        subject="美亚光电今日分析",
        body=content,
        to_emails=[receiver],
        auth_code=passwd,
    )

