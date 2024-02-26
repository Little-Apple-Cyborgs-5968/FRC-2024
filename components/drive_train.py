import rev
from wpilib import SmartDashboard
from sim.spark_sim import CANSparkMax
from wpilib import SPI
from wpilib.drive import MecanumDrive
from navx import AHRS
from wpimath.controller import PIDController
import time
from robot_map import CAN

class DriveTrain:
    def __init__(self, controller, LimeLight):
        # Intializes motors for the drive basse.
        self.frontRightMotor = CANSparkMax(CAN.frontRightChannel, rev.CANSparkMax.MotorType.kBrushless)
        self.rearRightMotor = CANSparkMax(CAN.rearRightChannel, rev.CANSparkMax.MotorType.kBrushless)
        self.frontLeftMotor = CANSparkMax(CAN.frontLeftChannel, rev.CANSparkMax.MotorType.kBrushless)
        self.rearLeftMotor = CANSparkMax(CAN.rearLeftChannel, rev.CANSparkMax.MotorType.kBrushless)
        self.frontRightMotor.restoreFactoryDefaults()
        self.rearRightMotor.restoreFactoryDefaults()
        self.frontLeftMotor.restoreFactoryDefaults()
        self.rearLeftMotor.restoreFactoryDefaults()
        self.frontRightMotor.setInverted(True)
        self.rearRightMotor.setInverted(True)

        # Sets up the controller and drive train.
        self.controller = controller
        self.robotDrive = MecanumDrive(self.frontLeftMotor, self.rearLeftMotor, self.frontRightMotor,
                                       self.rearRightMotor)
        self.gyroscope = AHRS(SPI.Port.kMXP)
        self.gyroscope.reset()
        self.LimeLight = LimeLight
        
        self.PIDInit()
        self.lastPIDExec = time.time()

    def autonomousInit(self):
        pass
    
    def autonomousPeriodic(self):
        pass
        self.putValues()

    def teleopInit(self):
        pass

    def teleopPeriodic(self):
        # Handles the movement of the drive base.
        deadband = 0.1
        if (abs(self.controller.getLeftY()) > deadband or abs(self.controller.getLeftX())) > deadband or abs(self.controller.getRightX()) > deadband:
            self.robotDrive.driveCartesian(
                self.controller.getLeftY(),
                self.controller.getLeftX(),
                self.controller.getRightX(),
                self.gyroscope.getRotation2d(),
            )
        else:
            self.robotDrive.driveCartesian(0, 0, 0, self.gyroscope.getRotation2d())
           
        if self.controller.getBackButton():
            self.gyroscope.reset()
        if self.controller.getPOV() == 90 and self.LimeLight.getNumber('tv'):
            self.pointAtTarget()
        if self.controller.getPOV() == 270 and self.LimeLight.getNumber('tv'):
            self.driveAtSpeaker()
            
        self.putValues()

    def putValues(self):
        SmartDashboard.putNumber("yaw", self.gyroscope.getYaw())
        SmartDashboard.putNumber("frontRightMotor", self.frontRightMotor.get())
        SmartDashboard.putNumber("frontLeftMotor", self.frontLeftMotor.get())
        SmartDashboard.putNumber("rearRightMotor", self.rearRightMotor.get())
        SmartDashboard.putNumber("rearLeftMotor", self.rearLeftMotor.get())

    def pointAtTarget(self):
        '''points toward current limelight target. Returns cursor offset'''
        tx = self.LimeLight.getNumber('tx', 0)
        self.PIDCalculate(-tx, 0, 0, 0)
        self.robotDrive.driveCartesian(0, 0, self.turnPIDVal)

    def driveAtSpeaker(self):
        '''drives toward speaker'''
        tx = self.LimeLight.getNumber('tx')        
        ANGLE = 15
        ty = self.LimeLight.getNumber('ty')
        self.PIDCalculate(-tx, ty, 0, ANGLE)
        self.robotDrive.driveCartesian(-self.drivePIDVal, 0, self.turnPIDVal)
        print(f"tx {tx} ty {ty}")

    
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

