import rev
from sim.spark_sim import CANSparkMax
from wpilib import SPI
from wpilib.drive import MecanumDrive
from navx import AHRS
from wpimath.controller import PIDController
import time
from robot_map import CAN
import wpimath
import wpimath.filter
import wpimath.controller
import math

kMaxSpeed = 3.0  # 3 meters per second
kMaxAngularSpeed = math.pi  # 1/2 rotation per second

class DriveTrain:
    def __init__(self, controller, LimeLight):
        # Intializes motors for the drive basse.
        self.frontRightMotor = CANSparkMax(CAN.frontRightChannel, rev.CANSparkMax.MotorType.kBrushless)
        self.rearRightMotor = CANSparkMax(CAN.rearRightChannel, rev.CANSparkMax.MotorType.kBrushless)
        self.frontLeftMotor = CANSparkMax(CAN.frontLeftChannel, rev.CANSparkMax.MotorType.kBrushless)
        self.rearLeftMotor = CANSparkMax(CAN.rearLeftChannel, rev.CANSparkMax.MotorType.kBrushless)
        # self.frontRightMotor.restoreFactoryDefaults()
        # self.rearRightMotor.restoreFactoryDefaults()
        # self.frontLeftMotor.restoreFactoryDefaults()
        # self.rearLeftMotor.restoreFactoryDefaults()
        self.frontRightMotor.setInverted(True)
        self.rearRightMotor.setInverted(True)

        # Sets up the controller and drive train.
        self.controller = controller
        self.robotDrive = MecanumDrive(self.frontLeftMotor, self.rearLeftMotor, self.frontRightMotor,
                                       self.rearRightMotor)
        self.gyroscope = AHRS(SPI.Port.kMXP)
        self.gyroscope.reset()
        self.LimeLight = LimeLight

        self.Shooterforward = True
        
        self.PIDInit()
        self.lastPIDExec = time.time()

    def autonomousInit(self):
        pass
    
    def autonomousPeriodic(self):
        pass

    def teleopInit(self):
        pass

    def teleopPeriodic(self):
        # Handles the movement of the drive base.
        self.driveWithJoystick(True)
           
        if self.controller.getBackButton():
            self.gyroscope.reset()
        # if self.controller.getPOV() == 90 and self.LimeLight.getNumber('tv'):
        #     self.pointAtTarget()
        # if self.controller.getAButton() and self.LimeLight.getNumber('tv'):
        #      self.driveAtSpeaker()
        if self.controller.getAButton():
            self.Shooterforward = not self.Shooterforward

    def drive(self, xSpeed, ySpeed, rot, fieldRelative):
        if fieldRelative:
            self.robotDrive.driveCartesian(
                xSpeed,
                ySpeed,
                rot,
                self.gyroscope.getRotation2d(),
            )
        else:
            self.robotDrive.driveCartesian(
                xSpeed,
                ySpeed,
                rot
            )

            

    def driveWithJoystick(self, fieldRelative: bool) -> None:
        # Get the x speed. We are inverting this because Xbox controllers return
        # negative values when we push forward.
        xSpeed = (
            -self.xspeedLimiter.calculate(
                wpimath.applyDeadband(self.controller.getLeftY(), 0.02)
            )
            * self.kMaxSpeed
        )

        # Get the y speed or sideways/strafe speed. We are inverting this because
        # we want a positive value when we pull to the left. Xbox controllers
        # return positive values when you pull to the right by default.
        ySpeed = (
            -self.yspeedLimiter.calculate(
                wpimath.applyDeadband(self.controller.getLeftX(), 0.02)
            )
            * self.kMaxSpeed
        )

        # Get the rate of angular rotation. We are inverting this because we want a
        # positive value when we pull to the left (remember, CCW is positive in
        # mathematics). Xbox controllers return positive values when you pull to
        # the right by default.
        rot = (
            -self.rotLimiter.calculate(
                wpimath.applyDeadband(self.controller.getRightX(), 0.02)
            )
            * self.kMaxSpeed
        )
        
        self.drive(xSpeed, ySpeed, rot, fieldRelative)

    # we are not using limelight vision processing
    def pointAtTarget(self):
        '''points toward current limelight target. Returns cursor offset'''
        tx = self.LimeLight.getNumber('tx', 0)
        self.PIDCalculate(-tx, 0, 0, 0)
        self.robotDrive.driveCartesian(0, 0, self.turnPIDVal)

    def driveAtSpeaker(self):
        '''drives toward speaker'''
        tx = self.LimeLight.getNumber('tx')        
        SPEED = 0.3
        ANGLE = 12.5
        ty = self.LimeLight.getNumber('ty')
        self.PIDCalculate(-tx, ty, 0, ANGLE)
        driveSpeed = -self.drivePIDVal * SPEED
        turnSpeed = self.turnPIDVal
        if abs(tx) < 1:
            driveSpeed = 0
        if abs(ty - ANGLE) < 1:
            turnSpeed = 0
        self.robotDrive.driveCartesian(driveSpeed, 0, turnSpeed)
        #print(f"tx {tx} ty {ty}")

    
    def PIDInit(self):
        self.turnPIDCam = PIDController(0.01, 0, 0.05)
        self.drivePIDCam = PIDController(0.05, 0, 0.1)
        self.turnPIDVal = 0
        self.drivePIDVal = 0
    
    def PIDCalculate(self, turnError = 0, driveError = 0, turnTarget = 0, driveTarget = 0):
        if time.time() - self.lastPIDExec > 100:
            self.PIDInit()
        self.turnPIDVal = self.turnPIDCam.calculate(turnError, turnTarget)
        self.drivePIDVal = self.drivePIDCam.calculate(driveError, driveTarget)
        self.lastPIDExec = time.time()

