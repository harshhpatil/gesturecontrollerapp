import cv2


class Webcam:
    """Handle webcam capture and display"""
    
    def __init__(self, index=1, width=1280, height=720):
        """
        Initialize webcam
        
        Args:
            index: Camera device index
            width: Frame width
            height: Frame height
        """
        self.cap = cv2.VideoCapture(index)
        
        if not self.cap.isOpened():
            raise RuntimeError(f"Cannot access camera at index {index}")
        
        # Set resolution for better performance
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        
        # Set FPS if supported
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        print(f"Camera initialized: {int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x"
              f"{int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))} @ "
              f"{int(self.cap.get(cv2.CAP_PROP_FPS))} FPS")

    def read(self):
        """
        Read frame from webcam
        
        Returns:
            Flipped frame or None if read fails
        """
        ret, frame = self.cap.read()
        if not ret:
            return None
        
        # Flip horizontally for mirror effect
        return cv2.flip(frame, 1)

    def show(self, frame):
        """Display frame in window"""
        cv2.imshow("Gesture Controller", frame)

    def is_opened(self):
        """Check if camera is still open"""
        return self.cap.isOpened()

    def release(self):
        """Release camera and close windows"""
        if self.cap.isOpened():
            self.cap.release()
        cv2.destroyAllWindows()
        print("Camera released")