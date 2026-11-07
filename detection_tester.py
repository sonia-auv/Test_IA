import cv2
import rclpy
from time import monotonic
from comparator import Comparator
from labeled_image import LabeledImage
from rclpy.node import Node
from rclpy.publisher import Publisher
from sensor_msgs.msg import Image
from sonia_common_ros2.msg import DetectionArray
from cv_bridge import CvBridge
from rosidl_runtime_py.convert import message_to_ordereddict

SUBSCRIBER_TIMEOUT = 5.0
RESPONSE_TIMEOUT = 5.0


class DetectionTester(Node):

    def __init__(self):
        super().__init__('detection_tester')
        self.pub: Publisher = self.create_publisher(Image, '/proc_simulation/front', 1)
        self.create_subscription(DetectionArray, '/proc_vision/front/classif', self.receive_results, 1)
        self.bridge = CvBridge()
        self.Images = list(LabeledImage.load_images())
        self.current_image: LabeledImage = self.Images.pop(0)
        self.timer_deadline = monotonic() + SUBSCRIBER_TIMEOUT
        self.timer = self.create_timer(1.0, self.__subscriber_check)
        self.response_timer = None


    def send_message(self):
        if self.response_timer:
            self.destroy_timer(self.response_timer)
        cv_image: cv2.typing.MatLike = cv2.imread(self.current_image.image_path)
        msg: Image = self.bridge.cv2_to_imgmsg(cv_image, encoding='bgr8')
        msg.header.frame_id = self.current_image.filename
        self.pub.publish(msg)
        self.response_timer = self.create_timer(RESPONSE_TIMEOUT, self.__response_timeout)


    def receive_results(self, msg: DetectionArray):
        if any(d.frame_id != self.current_image.filename for d in msg.detected_object):
            self.get_logger().error("Received detections for a different image.")
            rclpy.shutdown()
            return
        if not msg.detected_object:
            self.get_logger().error("Received empty response.")
            rclpy.shutdown()
            return
        result = list(message_to_ordereddict(detection) for detection in msg.detected_object)
        comparator: Comparator = Comparator(self.current_image.load_expected_results(), result)
        comparator.compare(self.current_image.filename)
        self.__next_image()


    def __next_image(self):
        if len(self.Images) == 0:
            rclpy.shutdown()
        else:
            self.current_image = self.Images.pop(0)
            self.send_message()


    def __response_timeout(self):
        self.get_logger().error(f"No response within {RESPONSE_TIMEOUT} seconds.")
        rclpy.shutdown()


    def __subscriber_check(self):
        if self.pub.get_subscription_count() > 0:
            self.destroy_timer(self.timer)
            self.send_message()
        elif monotonic() > self.timer_deadline:
            self.get_logger().error(f"No subscribers connected within {SUBSCRIBER_TIMEOUT} seconds.")
            rclpy.shutdown()