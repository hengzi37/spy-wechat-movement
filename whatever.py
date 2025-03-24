import os
import time
import cv2
from PIL import Image
import pytesseract
from datetime import datetime

x = 540
y = 1900
TARGET_NAME = "憨憨憨"
SCREENSHOT_DIR = "C:/Users/yyg/Desktop/aaa"
# 指定 Tesseract 的路径
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
os.environ["TESSDATA_PREFIX"] = r'C:\Program Files\Tesseract-OCR\tessdata'
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

# OCR 读取微信运动步数
def get_steps(screenshot_path):
    img = Image.open(screenshot_path)
    # 使用 Tesseract OCR 识别
    text = pytesseract.image_to_string(img, lang='chi_sim', config='--psm 6')  # 指定中文识别和页面分割模式
    print("OCR 识别结果：")
    print(text)  # 打印识别结果，方便调试

    # 查找包含"憨"字样的行
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if "憨" in line:  # 如果找到包含"憨"字样的行
            # 提取数字部分
            import re
            numbers = re.findall(r'\d+', line)
            if numbers:
                return int(numbers[-1])  # 返回最后一个数字（步数）
    return None  # 没找到
# ADB 截图 & 传输到电脑（按时间命名）
def capture_screenshot():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # 生成时间戳
    screenshot_path = os.path.join(SCREENSHOT_DIR, f"wechat_sport_{timestamp}.png")
    os.system("adb shell screencap -p /sdcard/wechat_sport.png")
    os.system(f"adb pull /sdcard/wechat_sport.png {screenshot_path}")
    return screenshot_path  # 返回截图路径
# 模拟滑动翻页，确保覆盖所有好友
def swipe_down():
    os.system("adb shell input swipe 500 1500 500 500")  # 从下往上滑
# 刷新页面
def reload():
    os.system("adb shell input keyevent 4")   #ESC
    time.sleep(5)  # 等待页面加载
    os.system(f"adb shell input tap {x} {y}")
    time.sleep(5)  # 等待页面加载


# 主程序
while True:
    reload()  # 刷新页面
    # 滑动直到找到目标昵称
    found = False
    max_swipes = 4  # 最大滑动次数，防止无限循环
    swipe_count = 0
    while not found and swipe_count < max_swipes:
        screenshot_path = capture_screenshot()  # 截图
        steps = get_steps(screenshot_path)  # 获取步数
        if steps is not None:
            print(f"{TARGET_NAME}  当前步数: {steps}")
            found = True
        else:
            swipe_down()  # 没找到就滑动
            swipe_count += 1
            time.sleep(2)  # 等待页面加载
    # 如果达到最大滑动次数仍未找到，输出提示
    if not found:
        print(f"未找到 {TARGET_NAME} 的步数")
    time.sleep(300)  # 5 分钟检查一次