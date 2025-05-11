import gradio as gr
import requests
import time

ESP32_IP = "http://172.20.10.8"
STREAM_URL = f"{ESP32_IP}:81/stream"
MOVE_URL = f"{ESP32_IP}/move"

def send_command(cmd):
    try:
        r = requests.get(f"{MOVE_URL}?dir={cmd}", timeout=0.3)
        return f"Sent: {cmd} | Response: {r.status_code}"
    except Exception as e:
        return f"Failed to send: {cmd} | Error: {e}"

def dance_mode():
    try:
        # 4x 90-degree turn (360 spin) using turnRight90 logic
        for _ in range(4):
            requests.get(f"{MOVE_URL}?dir=R", timeout=0.3)
            time.sleep(0.5)  # 90-degree delay (you can tweak this)
            requests.get(f"{MOVE_URL}?dir=S", timeout=0.3)
            time.sleep(0.2)

        # Move Backward for 2 seconds
        requests.get(f"{MOVE_URL}?dir=B", timeout=0.3)
        time.sleep(2)

        # Move Forward for 2 seconds
        requests.get(f"{MOVE_URL}?dir=F", timeout=0.3)
        time.sleep(2)

        # Stop
        requests.get(f"{MOVE_URL}?dir=S", timeout=0.3)
        return "Dance complete!"
    except Exception as e:
        return f"Dance command failed: {e}"

with gr.Blocks() as demo:
    gr.Markdown("## 🤖 Follow Me Robot Web UI")

    gr.HTML(f"""
        <h4>📷 Live ESP32-CAM Stream</h4>
        <img src="{STREAM_URL}" width="320" height="240" />
    """)

    with gr.Row():
        gr.Button("Forward").click(lambda: send_command("F"))
    with gr.Row():
        gr.Button("Left").click(lambda: send_command("L"))
        gr.Button("Stop").click(lambda: send_command("S"))
        gr.Button("Right").click(lambda: send_command("R"))
    with gr.Row():
        gr.Button("Backward").click(lambda: send_command("B"))
    with gr.Row():
        gr.Button("Dancing Mode").click(dance_mode)

demo.launch()