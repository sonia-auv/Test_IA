import rclpy
from detection_tester import DetectionTester


def main():
    node = None
    rclpy.init()
    try:
        node = DetectionTester()
        rclpy.spin(node)
    except (KeyboardInterrupt, rclpy.executors.ExternalShutdownException):
        pass
    finally:
        if node is not None:
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()