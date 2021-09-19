import cv2,time,pygame,numpy

interval = int(input("Введите интервал проверки в кадрах "))
threeshold = int(input("Введите порог разницы в цвете "))
threeshold_2 = float(input("Введите порог количества несовпадающих пикселей (в процентах от 0 до 1) "))
save_path = input("Введите путь к папке для сохранённых кадров (без / на конце) ")
path = input("(Пример: camera/Vorota.avi ) Введите путь ")
start_video = int(input("Введите время начала проверки "))
video_length = float(input("Введите длительность части видео в секундах "))

vidcap = cv2.VideoCapture(path)
(major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')
if int(major_ver)  < 3: fps = vidcap.get(cv2.cv.CV_CAP_PROP_FPS)
else: fps = vidcap.get(cv2.CAP_PROP_FPS)
vidcap.set(cv2.CAP_PROP_POS_FRAMES, start_video * fps )

fra = vidcap.read()[1]
vidcap.set(cv2.CAP_PROP_POS_FRAMES, start_video * fps + interval )



size = [len(fra[0]), len(fra)]

start = [0,0]
end = size

image = []
for i in range(size[0]):
    image.append([])
    for j in range(size[1]): image[i].append(fra[j,i])
image = numpy.array(image)

pygame.init()
screen = pygame.display.set_mode(size)
surface = pygame.pixelcopy.make_surface(image)
font = pygame.font.SysFont("Arial",16)
selecting_rect = True
stage = False
try:
    while selecting_rect:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                selecting_rect = False
            elif ev.type == pygame.MOUSEBUTTONDOWN:
                if not stage:
                    start = ev.pos
                    stage = True
                else:
                    end = ev.pos
                    pygame.quit()
                    selecting_rect = False
        screen.blit(surface,(0,0))
        mouse_pos = pygame.mouse.get_pos()
        if stage:
            pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(*start, mouse_pos[0]-start[0], mouse_pos[1]-start[1]), 1)
        text = font.render(str(mouse_pos), True, (255, 255, 255))
        screen.blit(text,(0,0))
        pygame.display.flip()
except: pass
pygame.quit()
size = [abs(end[0]-start[0]), abs(end[1]-start[1])]
threeshold_2_1 = size[0] * size[1] * threeshold_2

def compare_frames(frame_a, frame_b):
    global size
    count = 0
    for j in range(size[1]):
        for i in range(size[0]):
            for x in range(3):
                if frame_a[j,i,x] <= frame_b[j,i,x]-threeshold or frame_a[j,i,x] >= frame_b[j,i,x]+threeshold:
                    count += 1
                    break
    return True if count >= threeshold_2_1 else False

def crop_frame(frame):
    return frame[start[1]:end[1]+1,start[0]:end[0]+1]

def check_frame(frame_):
    global prev_check_frame
    result = False
    frame = crop_frame(frame_)
    result = compare_frames(prev_check_frame, frame)
    prev_check_frame = frame
    print("Completed check at {} second".format(int(count*interval/fps)))
    return result

prev_check_frame = crop_frame(fra)
count = 1
success = True

while success and (video_length == -1 or count*interval/fps < video_length):
    success,frame = vidcap.read()
    if check_frame(frame):
        s = count*interval/fps+start_video
        cv2.imwrite(save_path+"/frame{}-{}-{}.jpg".format(int(s/3600),int(s/60)%60,int((s%60)*10)/10), frame)
    count += 1
    vidcap.set(cv2.CAP_PROP_POS_FRAMES, start_video * fps + interval * count)
vidcap.release()
print("Ended processing")