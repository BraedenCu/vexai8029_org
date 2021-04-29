import jetson.inference
import jetson.utils

net = jetson.inference.detectNet("ssd-mobilenet-v2", threshold=0.5)
camera = jetson.utils.videoSource("/dev/video1")      # '/dev/video0' for V4L2
display = jetson.utils.videoOutput("display://0") # 'my_video.mp4' for file

width  = 320
height = 240
numDetections = 0

while display.IsStreaming():
    #img = camera.Capture()
    #detections = net.Detect(img)

    # Capture the image
    img = camera.Capture()
    # Detect objects in the image (with overlay?)
    detections = net.Detect(img, width, height)

    # Print the detections
    #print("detected {:d} objects in image".format(len(detections)))

    for detection in detections:
        numDetections += 1
        #print(detection)
        print("ID={0:02d}, L={1:.1f}, T={2:.1f}, R={3:.1f}, B={4:.1f}, W={5:.1f}, H={6:.1f}, A={7:.1f}, C={8:.1f}".format(detection.ClassID, detection.Left, detection.Top, detection.Right, detection.Bottom, detection.Width, detection.Height, detection.Area, detection.Confidence))
        # detection.Center.x, detection.Center.y  ???

    # Render the image
    display.Render(img)

    # Update the title bar
    display.SetStatus("Object Detection | Network {:.0f} FPS".format(net.GetNetworkFPS()))

    # Print out performance info
    #net.PrintProfilerTimes()

    if numDetections > 100:
        break

