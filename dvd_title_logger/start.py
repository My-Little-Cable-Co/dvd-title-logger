import PySimpleGUI as sg
import subprocess
import vlc
import json

sg.theme('DarkBlue15')

layout_l = [
    [sg.Button('Open Inserted Disc')],
    [sg.Button('Menu')],
    [sg.Button('Eject Disc')]
]

layout_r = [
    [sg.Image('', size=(640, 480), key='-VID_OUT-')],
    [sg.Output(s=(80,30))]
]

layout = [
    [sg.Col(layout_l, p=0), sg.Col(layout_r, p=0)]
]

# Create the Window
window = sg.Window('DVD Access Log', layout, finalize=True)

meta = {
    'title': None
}

def menu():
    vlc_player.set_title(0)

def get_mount_point():
    udf_mount_point = subprocess.run(["mount", "--types", "udf"], capture_output=True).stdout.decode().split(' ')[0]
    return udf_mount_point if udf_mount_point != '' else '/dev/sr1'

def get_dvd_info():
    result = subprocess.run(["dvd_info", "--json", mount_point], capture_output=True)
    dvd_info_output = result.stdout.decode()

    dvd_info_output_json = ''.join([line for line in dvd_info_output.splitlines() if not line.startswith('libdvdread: ')])
    dvd_info_json = json.loads(dvd_info_output_json)

    return dvd_info_json

def handle_title_change(event):
    current_title = vlc_player.get_title()
    if meta['title'] == current_title:
        return
    meta['title'] = current_title
    for title_index, title in enumerate(dvd_info['tracks']):
        if title['track'] == current_title:
            print(f"Title Changed: {title['track']} ({title['length']})")

def launch_vlc_and_track_events():
    vlc_instance = vlc.Instance()
    player = vlc_instance.media_player_new()

    player.set_xwindow(window['-VID_OUT-'].Widget.winfo_id())
    
    media = vlc_instance.media_new(f'dvdnav://{mount_point}')
    player.set_media(media)
    player.play()
    return player

def eject():
    print("Note: This doesn't work in my VM")
    print(subprocess.run(["eject", "-v"], capture_output=True).stdout.decode())


window.bind('<Left>', '-Left-')
window.bind('<Right>', '-Right-')
window.bind('<Up>', '-Up-')
window.bind('<Down>', '-Down-')
window.bind("<Return>", "-Enter-")
window.bind("<Escape>", "-Escape-")

# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED: # if user closes window or clicks cancel
        break
    if event == '-Left-':
        vlc_player.navigate(vlc.NavigateMode.left)
    if event == '-Right-':
        vlc_player.navigate(vlc.NavigateMode.right)
    if event == '-Up-':
        vlc_player.navigate(vlc.NavigateMode.up)
    if event == '-Down-':
        vlc_player.navigate(vlc.NavigateMode.down)
    if event == '-Enter-':
        vlc_player.navigate(vlc.NavigateMode.activate)
    if event == '-Escape-':
        menu()

    if event == 'Open Inserted Disc':
        mount_point = get_mount_point()
        dvd_info = get_dvd_info()
        print('Reading disc:\t\t' + dvd_info['dvd']['dvdread id'])
        print('DVD id:\t\t' + dvd_info['dvd']['title'] or 'Unknown Title')

        vlc_player = launch_vlc_and_track_events()
        events = vlc_player.event_manager()
        events.event_attach(vlc.EventType.MediaPlayerTitleChanged, handle_title_change)

    if event == 'Menu':
        menu()
    if event == 'Eject Disc':
        vlc_player.stop()
        eject()

window.close()

