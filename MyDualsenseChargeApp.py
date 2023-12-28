import time
import pystray
import threading
from PIL import Image, ImageDraw, ImageFont
from dualsense_controller import DualSenseController
import dualsense_controller.core.exception

MAX_DEVICES_AMOUNT: int = 4
need_exit: bool = False

dsense_normal_img = Image.open("img/dsense/normal.png")
dsense_dynamic_ico = dsense_normal_img.copy()
dsense_track_idx = 0
dsense_notconnected_img = Image.open("img/dsense/notconnected.png")
# dsense_full_img = Image.open("img/dsense/Full.png")
# dsense_threequarter_img = Image.open("img/dsense/75.png")
# dsense_half_img = Image.open("img/dsense/50.png")
# dsense_quarter_img = Image.open("img/dsense/25.png")
dsense_status_dict = ["Not inited", "Not inited", "Not inited", "Not inited"]


def tray_app_clicked_cb(sender, event):
    """
    Callback function when user presses some buttons in systray
    """
    global need_exit, dsense_track_idx
    if str(event) == "Exit":
        need_exit = True
        tray_app.stop()
        deactivate_all()
    elif "Dualsense" in str(event):
        dsense_track_idx = int(str(event)[str(event).find("#") + 1])


tray_app = pystray.Icon("MyDualsenseCharge", dsense_dynamic_ico, "MyDualsenseChargeApp",
                        menu=pystray.Menu(
                            pystray.MenuItem("Click on controller to monitor it in tray", None),
                            pystray.MenuItem("", None),
                            pystray.MenuItem(lambda text: dsense_status_dict[0], tray_app_clicked_cb),
                            pystray.MenuItem(lambda text: dsense_status_dict[1], tray_app_clicked_cb),
                            pystray.MenuItem(lambda text: dsense_status_dict[2], tray_app_clicked_cb),
                            pystray.MenuItem(lambda text: dsense_status_dict[3], tray_app_clicked_cb),
                            pystray.MenuItem("", None),
                            pystray.MenuItem("Exit", tray_app_clicked_cb)))


def deactivate_all():
    """
    Proper way to suddenly finish the program
    :return:
    """
    devices_enum = DualSenseController.enumerate_devices()

    if len(devices_enum) != 0:
        for device in range(len(devices_enum)):
            # TODO add try catch in case something will go wrong
            dsense = DualSenseController(device_index_or_device_info=device)
            if dsense.is_active:
                dsense.deactivate()
                time.sleep(1)


def redraw_percent(percentage: int):
    # FIXME could be done better. Especially font needs some job being done
    """
    Function for redrawing the systray icon for the tracked controller.
    :param percentage:
    :return:
    """
    global dsense_dynamic_ico
    font_size: int

    # Revert the icon to avoid text overlapping
    dsense_dynamic_ico = dsense_normal_img.copy()

    if percentage == -1:
        tray_app.icon = dsense_notconnected_img
        return
    elif percentage == 100:
        font_size = 22
    else:
        font_size = 30
    font = ImageFont.truetype("img/font/prstart.ttf", size=font_size)

    if percentage > 90:
        font_color = "#0000FF"
    elif 75 < percentage <= 90:
        font_color = "#00BB00"
    elif 50 < percentage <= 75:
        font_color = "#e0bb00"
    elif 25 < percentage <= 50:
        font_color = "#FF6000"
    else:
        font_color = "#FF0000"

    dsense_redraw = ImageDraw.Draw(dsense_dynamic_ico)
    dsense_redraw.text((0, 32), str(percentage), font=font, fill=font_color)
    # Uncomment only for debug
    # dsense_dynamic_ico.save("img/dsense/dsense_dynamic.png")
    tray_app.icon = dsense_dynamic_ico


def check_charging(dsense: DualSenseController, index: int):
    """
    Retrieve charging status of the DualSense controller, redraw systray icon if necessary.
    :param dsense: DualSenseController instance for parsing the data
    :param index:  Dualsense Contoller index from 0 to 3
    """
    global dsense_status_dict, dsense_track_idx
    batt = int(dsense.battery.value.level_percentage)
    is_charging = dsense.battery.value.charging

    if index == dsense_track_idx:
        redraw_percent(batt)
        dsense_status_dict[index] = f"[TRACKED] Dualsense #{index}: {batt}% | Charging: {is_charging}"
    else:
        dsense_status_dict[index] = f"Dualsense #{index}: {batt}% | Charging: {is_charging}"


def check_connected_controllers():
    """
    Function to check how many controllers are available.

    If controller is available, check it's charging state and redraw systray accordingly to it.
    """
    global dsense_status_dict, dsense_track_idx
    # Get connected devices enumeration
    devices_enum = DualSenseController.enumerate_devices()

    # If there are no devices available, update the tray accordingly
    if len(devices_enum) == 0:
        for device_idx in range(0, MAX_DEVICES_AMOUNT):
            # FIXME should be a better way than just copypaste
            # If we track this controller, write special tag
            if device_idx == dsense_track_idx:
                dsense_status_dict[device_idx] = f"[TRACKED] Dualsense #{device_idx}: Disconnected"
            else:
                dsense_status_dict[device_idx] = f"Dualsense #{device_idx}: Disconnected"
        redraw_percent(-1)
    else:
        for device_idx in range(len(devices_enum)):
            # TODO add try catch in case something will go wrong
            # Connect to the controller...
            dsense = DualSenseController(device_index_or_device_info=device_idx, microphone_initially_muted=False)
            dsense.activate()
            time.sleep(1)
            # ...and get its charging info
            check_charging(dsense, device_idx)
            time.sleep(1)
            dsense.deactivate()
        # Fill other inactive controller slots with the corresponding namings
        for device_idx in range(MAX_DEVICES_AMOUNT - 1, len(devices_enum) - 1, -1):
            if device_idx == dsense_track_idx:
                dsense_status_dict[device_idx] = f"[TRACKED] Dualsense #{device_idx}: Disconnected"
            else:
                dsense_status_dict[device_idx] = f"Dualsense #{device_idx}: Disconnected"
            # If we track the inactive device -- Draw "X" icon in systray
            if device_idx == dsense_track_idx:
                redraw_percent(-1)
    # Update all namings
    tray_app.update_menu()


def dualsense_thread_func():
    """
    Dualsense polling thread
    """
    while not need_exit:
        check_connected_controllers()
        time.sleep(3)
    exit()


def tray_thread_func():
    """
    Pystray systray loop thread
    """
    tray_app.run()


# Start thread for displaying the thread
tray_thread = threading.Thread(target=tray_thread_func)
tray_thread.start()

# Start thread for DualSense operations
dsense_thread = threading.Thread(target=dualsense_thread_func)
dsense_thread.start()
