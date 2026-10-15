import threading

try:
    import rospy
    from geometry_msgs.msg import Pose2D, Twist
    from std_msgs.msg import Bool
except Exception:
    rospy = None
    Pose2D = None
    Twist = None
    Bool = None

class ROSBridge:
    """ROS interface for the CyberDroneGame.

    Publishes the player's position and velocity, and subscribes to external
    command velocity and a shoot command. This enables a real robot to mirror the
    in‑game drone and allows external ROS nodes to control the game.
    """

    def __init__(self, namespace: str = "cyber_drone"):
        if rospy is None:
            self.enabled = False
            return
        self.enabled = True
        self.ns = namespace.rstrip('/')
        rospy.init_node(self.ns + "_bridge", anonymous=True, disable_signals=True)
        self.pose_pub = rospy.Publisher(self.ns + "/pose", Pose2D, queue_size=10)
        self.vel_pub = rospy.Publisher(self.ns + "/velocity", Twist, queue_size=10)
        self.cmd_vel_sub = rospy.Subscriber(self.ns + "/cmd_vel", Twist, self._cmd_vel_cb)
        self.shoot_sub = rospy.Subscriber(self.ns + "/shoot", Bool, self._shoot_cb)
        self._lock = threading.Lock()
        self._latest_cmd = Twist()
        self._latest_shoot = False

    def _cmd_vel_cb(self, msg: Twist):
        with self._lock:
            self._latest_cmd = msg

    def _shoot_cb(self, msg: Bool):
        with self._lock:
            self._latest_shoot = bool(msg.data)

    def get_latest_commands(self):
        """Return the most recent cmd_vel and shoot flag.
        Caller should acquire the lock via this method's internal lock.
        """
        with self._lock:
            cmd = Twist()
            cmd.linear.x = self._latest_cmd.linear.x
            cmd.linear.y = self._latest_cmd.linear.y
            cmd.angular.z = self._latest_cmd.angular.z
            shoot = self._latest_shoot
        return cmd, shoot

    def publish_state(self, player) -> None:
        if not self.enabled:
            return
        pose = Pose2D()
        pose.x = player.x
        pose.y = player.y
        pose.theta = 0.0
        self.pose_pub.publish(pose)
        twist = Twist()
        twist.linear.x = player.vx
        twist.linear.y = player.vy
        twist.angular.z = 0.0
        self.vel_pub.publish(twist)

    def apply_commands_to_player(self, player) -> None:
        if not self.enabled:
            return
        cmd, shoot = self.get_latest_commands()
        player.vx = cmd.linear.x
        player.vy = cmd.linear.y
        if shoot:
            if hasattr(player, 'fire'):
                player.fire()
            with self._lock:
                self._latest_shoot = False
