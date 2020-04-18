# VideoToChar

## 利用python实现的视频字符化小程序

涉及到的第三方库有：

```
opencv`，`PIL`，`moviepy`，`theading
```

没有安装的请自行pip安装

main函数三个参数分别为(原始视频路径,字符视频名称,最终视频名称)

其中第二个参数字符视频名称为中间过程产品，导出的视频是没有声音的

## 处理前后对比：

![2018_Moment](C:\Users\1696589321\Desktop\2018_Moment.jpg)



![char_2018_gray_Moment](C:\Users\1696589321\Desktop\char_2018_gray_Moment.jpg)



![char_2018_normal_Moment](C:\Users\1696589321\Desktop\char_2018_normal_Moment.jpg)

## 目前只是一个雏形，只可以实现代码将视频字符化，后续会添加GUI(PyQt5)，敬请期待