import cv2
import os
import threading
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import concatenate_videoclips, VideoFileClip

chars = list("$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,\"^`'. ")

frames = r"..\pictures\\"
frames_char = r"..\pitcures_char\\"

width, height, fps, count = [None] * 4


def get_video(pathv):
    """
    导入视频
    :param pathv:视频路径
    :return: None
    """
    global width, height, fps, count
    vc = cv2.VideoCapture(pathv)  # 导入视频
    frame_No = 0  # 帧编号
    ret = vc.isOpened()  # 判断载入的视频是否可以打开
    # 获取视频参数
    fps = vc.get(cv2.CAP_PROP_FPS)
    count = vc.get(cv2.CAP_PROP_FRAME_COUNT)
    width = int(vc.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(vc.get(cv2.CAP_PROP_FRAME_HEIGHT))
    while ret:
        ret, frame = vc.read()
        if ret:
            cv2.imwrite(frames + str(frame_No) + '.jpg', frame)
            frame_No += 1
            cv2.waitKey(1)  # 1ms延时
        else:
            break
    vc.release()


def get_char(r, g, b, alpha=256):
    """
    根据每一帧的RGB获取每种颜色对应的字符
    :param r: R
    :param g: G
    :param b: B
    :param alpha: Alpha
    :return: Integer
    """
    if alpha == 0:
        return ' '
    return chars[int(int(0.2126 * r + 0.7152 * g + 0.0722 * b) / ((256.0 + 1) / len(chars)))]


def get_frame_char(begin=0, end=count, is_gray=True):
    """
    将每一帧转化为字符
    :param begin: 开始帧位置
    :param end: 结束帧位置
    :param is_gray: 是否为灰色，默认为True
    :return: picture
    """
    for frame_No in range(begin, end):
        print("正在处理第{}帧".format(frame_No))
        img = frames + str(frame_No) + ".jpg"
        if os.path.exists(img):
            im = Image.open(img).convert('RGB')  # 将图片转化为RGB格式
            new_width = int(im.width)
            new_height = int(im.height)
            # 获取设定的字体的尺寸，ImageFont默认的尺寸大小为6x11，其他字体会有所不同
            # 此处使用的字体为truetype字体，大小为10px
            font = ImageFont.truetype('consola.ttf', 10, encoding='unic')
            font_x, font_y = font.getsize(' ')
            # 确定单元的大小
            unit_width = int(font_x)
            unit_height = int(font_y)
            # 确定长宽各有几个单元
            w = int(new_width / unit_width)
            h = int(new_height / unit_height)
            # 将每个单元缩小为一个像素
            im = im.resize((w, h), Image.NEAREST)
            # txts和colors分别存储对应块的ASCII字符和RGB值
            txts = []
            colors = []
            for i in range(h):  # 遍历行
                line = ''
                lineColor = []
                for j in range(w):  # 遍历列
                    pixel = im.getpixel((j, i))
                    lineColor.append((pixel[0], pixel[1], pixel[2]))
                    line += get_char(pixel[0], pixel[1], pixel[2])
                txts.append(line)
                colors.append(lineColor)
            # 创建新画布
            im_txt = Image.new("RGB", (new_width, new_height), (255, 255, 255))
            # 创建ImageDraw对象以写入ASCII
            draw_handle = ImageDraw.Draw(im_txt)
            for j in range(len(txts)):
                for i in range(len(txts[j])):
                    if is_gray:  # 灰色
                        draw_handle.text((i * unit_width, j * unit_height), txts[j][i], (50, 50, 50))
                    else:  # 原色
                        draw_handle.text((i * unit_width, j * unit_height), txts[j][i], colors[j][i])
            name = frames_char + str(frame_No) + '.jpg'
            im_txt.save(name, 'JPEG')


def severalThreadings(isgray=True):
    """
    多线程处理灰度图像
    :param isgray: 是否为灰色，默认为True
    :return: pictures
    """
    lines = 5
    eachPice = int(count / lines)  # 每个线程所需处理帧数
    threads = []
    for line in range(lines):  # 对于一片进行处理，然后计算扩展到
        begin = line * eachPice
        end = (line + 1) * eachPice
        if line == lines - 1:  # 如果是最后一个线程，则其工作为收尾工作，将图片进行到最后
            end = int(count)
        thread = threading.Thread(target=get_frame_char, args=(begin, end, isgray))
        threads.append(thread)
        thread.setDaemon(True)
        thread.start()
    for item in threads:
        item.join()


def create_video(pathv):
    # 输出视频参数设置,包含视频文件名、编码器(MJPG)、帧率、视频宽高(此处和字符图片大小一致)
    video_writer = cv2.VideoWriter(pathv, cv2.VideoWriter_fourcc(*'MJPG'), fps, (width, height))
    for i in range(1, 1000):
        filename = frames_char + str(i) + '.jpg'
        if os.path.exists(filename):  # 图片存在
            img = cv2.imread(filename=filename)
            cv2.waitKey(100)  # 延时1ms
            video_writer.write(img)  # 将图片写入视频中
    video_writer.release()


def add_audio(initial_video, char_video, end_video):
    """
    添加音频
    :param initial_video: 原始视频路径
    :param char_video: 字符视频名称
    :param end_video: 最终视频名称
    :return: video
    """
    ini_video = VideoFileClip(initial_video)  # 原始视频
    audio = ini_video.audio  # 提取音频
    # audio.write_audiofile(initial_video+".mp3")  # 保存音频
    ch_video = VideoFileClip(char_video)  # 字符视频
    ch_video1 = ch_video.set_audio(audio)  # 字符视频添加音频
    ch_video2 = concatenate_videoclips([ch_video1])
    ch_video2.write_videofile(end_video)
    # 也可以一行代码解决：
    # concatenate_videoclips([VideoFileClip(char_video).set_audio(VideoFileClip(initial_video).audio)]).write_videofile()


def main(pathv, charv, endv, isgray=True):
    """
    主函数
    :param pathv: 原始视频路径
    :param charv: 字符视频名称
    :param endv: 最终视频名称
    :param isgray: 是否灰色，默认为True
    :return: video
    """
    if not os.path.exists(frames):
        os.mkdir(frames)
    if not os.path.exists(frames_char):
        os.mkdir(frames_char)
    get_video(pathv)
    severalThreadings(isgray=isgray)
    create_video(charv)  # 生成字符视频
    add_audio(pathv, charv, endv)  # 字符视频添加音频
    os.system("rd /s /q " + frames)
    os.system("rd /s /q " + frames_char)


if __name__ == '__main__':
    main("2018.mp4", "silent_2018_gray.mp4", "char_2018_gray.mp4", isgray=True)
    # main("2018.mp4", "silent_2018_normal.mp4", "char_2018_normal.mp4", isgray=False)
