import sensor, image, time, gc, math

def highPassFilter(img1, limit, rgb):
    for pixel_y in range(img1.height()):
        for pixel_x in range(img1.width()):
            pixel = img1.get_pixel(pixel_x, pixel_y)
            if(limit > pixel[rgb]):
                img1.set_pixel(pixel_x, pixel_y,(0,0,0))
    return img1

def lowPassFilter(img1, limit, rgb):
    rgb1 = (rgb + 1) % 3
    rgb2 = (rgb + 2) % 3
    for pixel_y in range(img1.height()):
        for pixel_x in range(img1.width()):
            pixel = img1.get_pixel(pixel_x, pixel_y)
            if(limit < pixel[rgb1] or limit < pixel[rgb2]):
                img1.set_pixel(pixel_x, pixel_y,(0,0,0))
    return img1

def red2white(img1, limit, rgb):
    for pixel_y in range(img1.height()):
        for pixel_x in range(img1.width()):
            pixel = img1.get_pixel(pixel_x, pixel_y)
            if(limit < pixel[rgb]):
                img1.set_pixel(pixel_x, pixel_y,(255,255,255))
    return img1

def findAngle(area, inImg):
    #lines = inImg.find_lines(threshold=1400, x_stride=2, y_stride=2, theta_margin=4, rho_margin=5)
    lines = inImg.find_line_segments(threshold=5000, merge_distance=5, max_theta_difference=2)
    angle = 0
    maxLength = 0
    for item in lines:
        if(item[4] > 4):
            inImg.draw_line(item[0], item[1], item[2], item[3], color=(0,255,0), thickness=1)
            print(item)
            if(maxLength < item[4]):
                maxLength = item[4]
                angle = item.theta()
    return angle

def findCircleXY(img, highpass, lowpass, rgb):
    workImg = img.copy()
    workImg = workImg.cartoon(0.3, 0.2)
    workImg = workImg.bilateral(1, color_sigma=1.5, space_sigma=0.5)
    highPassFilter(workImg, highpass, rgb)

    img.draw_image(workImg,0,0)
    sensor.snapshot()

    print("lowPassFilter")
    lowPassFilter(workImg, lowpass, rgb)
    img.draw_image(workImg,0,0)
    sensor.snapshot()

    workImg = workImg.to_grayscale()
    gc.collect()

    obj = workImg.find_circles(x_stride=1, y_stride=1, threshold=2800)
    print(obj);
    circleX = 0
    circleY = 0
    if len(obj) > 0:
        for index, item in enumerate(obj):
            if(item[2] < 25 and item[2] > 10):
                workImg.draw_circle(item[0], item[1], item[2], thickness=2);
                circleX = item[0]
                circleY = item[1]

    img.draw_image(workImg,0,0)
    sensor.snapshot()
    print("X: " + str(circleX) + ",    Y: " + str(circleY))
    return [circleX, circleY]

print("0")
gc.collect()
sensor.reset()
sensor.set_vflip(True)
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QQVGA)
sensor.skip_frames(time = 1000)
clock = time.clock()
clock.tick()

print("1")
img = sensor.snapshot()
xy1 = findCircleXY(img, 60, 120, 1)    #for green circle
print(xy1)
img = sensor.snapshot()
xy2 = findCircleXY(img, 60, 140, 2)    #for blue circle
print("green: " + str(xy1))
print(xy2)

img.draw_line(xy1[0],xy1[1],xy2[0],xy2[1])
angle = math.atan2(xy2[1] - xy1[1], xy2[0] - xy1[0])
angle = angle * math.pi    #convert radian to degree
angle = -angle + 90
print("C1-C2 angle: " + str(angle))


while(True):
    clock.tick()

    img = sensor.snapshot()
    print("width: " + str(img.width()))
    print("2")
    img2 = img.copy((20,20,img.width(), img.height()))
    #img2 = img2.flood_fill(0,0)
    #img2 = img2.cartoon(0.3, 0.2)
    img2 = highPassFilter(img2, 50, 0)    #0:r, 1:g, 2:b
    img2 = lowPassFilter(img2, 100, 0)

    img.draw_image(img2, 10,10)
    sensor.snapshot()
    time.sleep(2)

    img2 = img2.cartoon(0.5, 0.5)
    img.draw_image(img2, 10,10)
    sensor.snapshot()
    time.sleep(2)

    img2 = img2.bilateral(1, color_sigma=0.8, space_sigma=1.1)
    img.draw_image(img2, 10,10)
    sensor.snapshot()
    time.sleep(2)

    #img2 = img2.dilate(2, threshold=10)
    #img2 = img2.flood_fill(0,0, seed_threshold=0.05, floating_threshold=0.1, clear_backgroud=False)
    #img.find_edges(image.EDGE_CANNY)
    #img = red2white(img, 100, 0)
    gc.collect()
    print("3");
    area = 0,0,200,100
    findResult = findAngle(area, img2)
    print("angle: " + str(findResult))
    print("width: " + str(img2.width()))
    img.draw_image(img2,10,10)
    sensor.snapshot()

    time.sleep_ms(500)
    print(clock.fps())

