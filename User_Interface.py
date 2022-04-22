from fileinput import filename
from socket import timeout
import PySimpleGUI as sg
import cv2
import numpy as np

from camera_cv import run_cv, ui_wid, ui_cook_t

def set_size(element, size):
    # From https://github.com/PySimpleGUI/PySimpleGUI/issues/4407
    # Only work for sg.Column when `scrollable=True` or `size not (None, None)`
    options = {'width':size[0], 'height':size[0]}
    if element.Scrollable or element.Size!=(None, None):
        element.Widget.canvas.configure(**options)
    else:
        element.Widget.pack_propagate(0)
        element.set_size(size)

def main():
    sg.theme("Dark Red")

    # cam_feed = [sg.Image(filename='', key="cam_feed")]
    detected_thickness = "0.25 inches"
    time_to_cook = "1:00 minutes"
    section_placement = "2"
    camera_Width  = 320 # 480 # 640 # 1024 # 1280
    camera_Height = 240 # 320 # 480 # 780  # 960
    frameSize = (camera_Width, camera_Height)
    recording = True
    # recording = False


    welcome_page = [
        [
            # sg.Text(text="\nKBBQ for KBBeginners", justification="center", font=("Arial", 20), size=(30, 3), expand_x=True, expand_y=True, auto_size_text=True)
            sg.Text("\nKBBQ for KBBeginners", justification="center", font=("Arial", 20), size=(30, 3), expand_x=True, expand_y=True)
        ],
        [
            sg.Button("Automatic", font=("Arial", 16), size=(16,3), pad=(23,28), expand_x=True, expand_y=True),
            sg.Button("Manual", font=("Arial", 16), size=(16,3), pad=(23,28), expand_x=True, expand_y=True)
        ],
        # cam_feed
    ]

    auto_info_column = [
        [sg.Text("New Meat Info:\n", justification="center", font=("Arial", 30), expand_x=True, expand_y=True)],

        [sg.Text("Detected Thickness:", justification="center", font=("Arial", 20), expand_x=True, expand_y=True)],
        [sg.Text(detected_thickness, justification="center", font=("Arial", 20), expand_x=True, expand_y=True)],

        [sg.Text("Time to Cook:", justification="center", font=("Arial", 20), expand_x=True, expand_y=True)],
        [sg.Text(time_to_cook, justification="center", font=("Arial", 20), expand_x=True, expand_y=True)],

        [sg.Text("Section Placement:", justification="center", font=("Arial", 20), expand_x=True, expand_y=True)],
        [sg.Text(section_placement, justification="center", font=("Arial", 20), expand_x=True, expand_y=True)]
    ]

    cam_feed_page = [
        [
            sg.Text("KBBQ for KBBeginners\n", justification="center", font=("Verdana", 40), expand_x=True)
        ],
        [
            sg.Column(auto_info_column, pad=50),
            # sg.Image("nyan.gif", expand_x=True, expand_y=True),
            # sg.Graph(canvas_size=(720,440), key="graph", graph_bottom_left=(0,0), graph_top_right=(720,440), background_color="gray"),
            # sg.Graph(canvas_size=(480,360), key="graph",expand_x=True, expand_y=True, graph_bottom_left=(0,0), graph_top_right=(480,360), background_color="gray")
            # sg.Graph(canvas_size=(800, 480), key="graph",expand_x=True, expand_y=True, graph_bottom_left=(0,0), graph_top_right=(800,440))
            # sg.Image(filename='', key="cam_feed", expand_x=True, expand_y=True)
            sg.Image(filename='', key="cam_feed")
            # sg.Image(filename='', key="cam_feed", size=(480,360), expand_x=True, expand_y=True)
        ],
    ]

    layout = [
        # [sg.Column(welcome_page, key="welcome_page", visible=True, size=(640,480))],
        # [sg.Column(welcome_page, key="welcome_page", visible=True, element_justification='center', vertical_alignment='center')],
        # [sg.Column(welcome_page, key="welcome_page", visible=True, element_justification='center', vertical_alignment='center', expand_x=True, expand_y=True)],
        # [sg.Column(cam_feed_page, key="cam_feed_page", visible=False, size=(640,480))]
        [sg.Column(cam_feed_page, key="cam_feed_page", visible=True, element_justification='center', vertical_alignment='center')],
        # [sg.Image(filename='', key="cam_feed")]
    ]

    # window = sg.Window(title="KBBQ for KBBeginners", layout=layout, margins=(10, 10), size=(640, 480))
    window = sg.Window("KBBQ for KBBeginners", layout=layout, margins=(10, 10), resizable=True).finalize()
    window.maximize()

    # graph = window.Element("graph")
    # # graph.DrawImage(filename="", location=(0,440))
    # # graph.DrawImage(filename="nyan.gif", location=(0,440))
    # # graph.DrawImage(filename="nyan.gif", location=(80, 280))
    # graph.DrawRectangle((0,1), (719,440))
    # graph.DrawLine((360,0), (360,440))
    # graph.DrawLine((0, 220), (720,220))
    # graph.DrawText("1", (180, 420), font="Arial 20")
    # graph.DrawText("2", (540, 420), font="Arial 20")
    # graph.DrawText("3", (180, 200), font="Arial 20")
    # graph.DrawText("4", (540, 200), font="Arial 20")
    # graph.DrawButton

    # set_size(window['welcome_page'], (window.size))
    # set_size(window['cam_feed_page'], (window.size))
    # sg.Window(title="KBBQ for KBBeginners", layout=[[]], margins=(341.5, 256)).read()

    video = cv2.VideoCapture(0) #change to 1 for external camera
    # window.bind('<Configure>',"resize")

    while True:
        # event, values = window.read()
        event, values = window.read(timeout=20)
        
        if event == sg.WIN_CLOSED:
            break
        # if event == "Automatic":
        #     # window = sg.Window(title="Automatic", layout = cam_feed_page, margins=(10,10))
        #     # window["welcome_page"].update(visible=False)
        #     set_size(window['welcome_page'], (0,0))
        #     # set_size(window['cam_feed_page'], window.size)
        #     window["cam_feed_page"].update(visible=True)
        #     # recording=True
        #     # window.layout = cam_feed_page
        #     # break
        # img = np.full((480, 640), 255)
        # # this is faster, shorter and needs less includes
        # imgbytes = cv2.imencode('.png', img)[1].tobytes()
        # window['cam_feed'].update(data=imgbytes)
        # if event == "resize" and not recording:
        #     set_size(window['welcome_page'], (window.size))

        # if event == "resize" and recording:
        if event == "resize":
            set_size(window['cam_feed_page'], (window.size))

        if recording:
            # ret, frameOrig = video.read()
            ret, frame = video.read()
            # frame = cv2.resize(frameOrig, frameSize)
            # frame=np.full((480,640),255)

            run_cv()

            imgbytes = cv2.imencode(".png", frame)[1].tobytes()
            # window["graph"].update(data=imgbytes)
            window["cam_feed"].update(data=imgbytes)

    # video.release()
    # cv2.destroyAllWindows()

main()