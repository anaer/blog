```py
# -*-coding:utf-8-*-
# chrome for testing: https://registry.npmmirror.com/binary.html?path=chrome-for-testing/114.0.5735.90/
# chromedrive: https://registry.npmmirror.com/binary.html?path=chromedriver/114.0.5735.90/
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

chrome_options = Options()
chrome_options.add_argument("--headless=new")      # 无头模式
chrome_options.add_argument("--no-sandbox")        # 禁用沙箱
chrome_options.add_argument("--disable-dev-shm-usage") # 解决共享内存问题
chrome_options.add_argument("--disable-gpu")       # 禁用 GPU 加速
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"]) # 移除 "自动化控制" 提示
chrome_options.add_experimental_option('useAutomationExtension', False) # 禁用自动化扩展

# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.chrome.service import Service


def get_element_value():
    # 1. 初始化 Chrome 浏览器
    # 如果你没有配置环境变量，需要在括号内指定 chromedriver 的路径
    #driver = webdriver.Chrome()
    #driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver = webdriver.Chrome(options=chrome_options)

    # 3. 执行 CDP 命令，彻底隐藏 webdriver 属性 (关键步骤)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": """
        Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
        })
    """
    })

    try:
        # 2. 打开目标网页
        url = "https://quote.abc.com/q/123.html" # 示例URL，请替换为你实际的目标网址
        print(f"正在访问: {url}")
        driver.get(url)

        # 3. 设置显式等待
        # 这一步非常关键，因为 Selenium 渲染页面需要时间
        wait = WebDriverWait(driver, 10)
        # element = wait.until(
        #     EC.presence_of_element_located((By.CLASS_NAME, "quote_quotenums"))
        # )

        css_selector = "div.quote_quotenums > div.zxj > span:nth-child(1) > span"

        element = wait.until(
            lambda d: d.find_element(By.CSS_SELECTOR, css_selector).text.strip() != ""
        )

        # 4. 获取元素的值
        # 情况A: 如果 "zxj" 是输入框(input)，获取用户输入的值用 .get_attribute('value')
        # 情况B: 如果 "zxj" 是普通标签(如 span, div)，获取包裹的文本用 .text

        element = driver.find_element(By.CLASS_NAME, "quote_quotenums")
        text_value = element.text
        print(f"成功获取 class='quote_quotenums' 的文本内容: {text_value}")

    except TimeoutException:
        print("错误：在 10 秒内未找到目标元素，页面加载可能过慢或元素不存在。")
    finally:
        # 5. 关闭浏览器，释放资源
        driver.quit()
        print("浏览器已关闭。")

if __name__ == "__main__":
    get_element_value()

```