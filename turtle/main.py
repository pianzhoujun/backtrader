from datetime import datetime
from datetime import timedelta
import pandas as pd
import sma_detector as sdet
import sma
import markdown

from llm_agent import ask_llm

try:
    # load environment variables from .env file (requires `python-dotenv`)
    from dotenv import load_dotenv
    load_dotenv(dotenv_path="./.env", override=True)
except ImportError:
    pass

import os 
sender = str(os.environ.get("EMAIL_SENDER"))
receiver = str(os.environ.get("EMAIL_RECEIVER"))
passwd = str(os.environ.get("EMAIL_PASSWD"))

stocks = {
    "HS300": "data/hs300_stocks.csv",
    "ZZ500": "data/zz500_stocks.csv"
}

def send_mail(subject, content):
    import notification
    notification.send_email_smtp(
        subject=subject,
        body=content,
        to_emails=[receiver],
        auth_code=passwd,
    )

def format_email_content(content: list[tuple]) -> str:
    """
    Description: 
       content is a list of tuple, each tuple contains 4 elements: code, name, profit, win_prob.
       format the content to html table format.
    Args:
        content (list[tuple]): [stock code, stock name, profit, win prob] 
    Returns:
        str: html content for email.
    """
    if not content:
        return "<p>暂无选股结果。</p>"

    html = """
    <html>
    <body>
    <h3>今日量化选股结果：</h3>
    <table border="1" cellpadding="6" cellspacing="0" style="border-collapse: collapse; font-family: Arial, sans-serif;">
        <tr style="background-color: #f2f2f2;">
            <th>代码</th>
            <th>名称</th>
            <th>回测收益/th>
            <th>回测收益率th>
            <th>胜率</th>
        </tr>
    """

    for code, name, avg_profit, avg_profit_ratio, win_prob in content:
        html += f"""
        <tr>
            <td>{code}</td>
            <td>{name}</td>
            <td>{avg_profit:.2f}</td>
            <td>{avg_profit_ratio:.2f}</td>
            <td>{win_prob:.2f}</td>
        </tr>
        """

    html += """
    </table>
    <p>以上为今日策略回测结果，请注意风险控制。</p>
    </body>
    </html>
    """

    return html

def main():
    print("Starting SMA Detector")
    end_date    = datetime.today()
    start_date  = end_date - timedelta(days=365)
    start_date  = start_date.strftime("%Y-%m-%d")
    end_date    = end_date.strftime("%Y-%m-%d")
    
    stock_to_ask_llm = []
    
    content = []

    for stock_cls, stock_csv in stocks.items():
        print(f"Begin detect {stock_cls} golden crosses...")
        sdet.run(start_date, end_date, stock_csv, 2)
        print("Detect golden crosses done.")
        print("Do SMA Backtrade analysis...")

        df = pd.read_csv('data/golden_cross.csv', encoding='utf-8',parse_dates=['Last Cross Date'])
        for _, row in df.iterrows():
            code = row['Code']
            data = pd.read_csv(f'data/{code}.csv', parse_dates=['date'])
            avg_profit, avg_profit_ratio, win_prob = sma.runstrat(data)
            if avg_profit_ratio >= 0.02 and win_prob >= 0.5:
                print(f"sma 🎉 盈利: {code} {row['Name']}. avg profit={avg_profit:.2f}. avg profit ratio = {avg_profit_ratio:.2f}. win probability={win_prob:.2f}")
                content.append((code, row['Name'], avg_profit, avg_profit_ratio, win_prob))
                stock_to_ask_llm.append((code, row['Name'], avg_profit, avg_profit_ratio, win_prob))

        print("SMA Backtrade analysis done.")
        print(f"Finish {stock_cls}")
        print("....................................")

    send_mail(f"{end_date} SMA分析结果", format_email_content(content))

    if False and len(stock_to_ask_llm) > 0:
        for code, name, _, _, _ in stock_to_ask_llm:
            content = [] 
            content.append(f"\n## code: {code}, name: {name}. \n")
            content.append(ask_llm(code))
            content = markdown.markdown('\n'.join(content))
            send_mail(f"{end_date} {code} {name} AI分析结果", content)
    print("Done. And good luck!")

if __name__ == "__main__":
    main()
