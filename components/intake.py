import rev

from robot_map import CAN

class Intake:
    def __init__(self, controller):
        # Intializes motor
        self.pivotMotorOne = rev.CANSparkMax(CAN.pivotOneChannel, rev.CANSparkMax.MotorType.kBrushless)
        self.pivotMotorTwo = rev.CANSparkMax(CAN.pivotTwoChannel, rev.CANSparkMax.MotorType.kBrushless)
        self.intakeMotorTwo = rev.CANSparkMax(CAN.intakeTwoChannel, rev.CANSparkMax.MotorType.kBrushless)
        self.intakeMotorTwo = rev.CANSparkMax(CAN.intakeTwoChannel, rev.CANSparkMax.MotorType.kBrushless)

        self.pivotMotorOne.restoreFactoryDefaults()
        self.pivotMotorTwo.restoreFactoryDefaults()
        self.intakeMotorOne.restoreFactoryDefaults()
        self.intakeMotorTwo.restoreFactoryDefaults()

        self.pivotPIDControllerOne = self.pivotMotorOne.getPIDController()
        self.pivotPIDControllerOne.setP(0.5) # Don't use these values
        self.pivotPIDControllerOne.setI(0.0)
        self.pivotPIDControllerOne.setD(7)
        self.pivotPIDControllerOne.setFF(0.0)
        self.pivotChannelOne = self.pivotMotorOne.getEncoder()

        self.pivotPIDControllerTwo = self.pivotMotorTwo.getPIDController()
        self.pivotPIDControllerTwo.setP(0.5) # Don't use these values
        self.pivotPIDControllerTwo.setI(0.0)
        self.pivotPIDControllerTwo.setD(7)
        self.pivotPIDControllerTwo.setFF(0.0)
        self.pivotChannelTwo = self.pivotMotorTwo.getEncoder()

        self.controller = controller

        self.intake_speed = 0.2
        
    def autonomousInit(self):
        pass
    
    def autonomousPeriodic(self):
        pass

    def teleopInit(self):
        self.pivotPIDControllerOne.setPosition(0)
        self.pivotPIDControllerTwo.setPosition(0)
        self.pivotOnePosition = 0
        self.pivotTwoPosition = 0

         # Sets PID values for teleoperated.
        self.pivotPIDControllerOne.setP(0.5)
        self.pivotPIDControllerOne.setI(0.0)
        self.pivotPIDControllerOne.setD(7)
        self.pivotPIDControllerOne.setFF(0.0)

        self.pivotPIDControllerTwo.setP(0.5)
        self.pivotPIDControllerTwo.setI(0.0)
        self.pivotPIDControllerTwo.setD(7)
        self.pivotPIDControllerTwo.setFF(0.0)

    def teleopPeriodic(self):
        # Handles the movement of the drive base.
        # Handles control on the intake motor.
        if self.controller.getAButton():
            self.intakeMotorOne.set(self.intakeSpeed)
            self.intakeMotorOne.set(self.intakeSpeed)
        elif self.controller.getPOV() == 0:
            self.intakeMotorOne.set(-self.intakeSpeed)
            self.intakeMotorOne.set(-self.intakeSpeed)
        else:
            self.intakeMotorOne.set(0)
            self.intakeMotorTwo.set(0)
    
        # Handles control on the shoulder motor.
        if self.controller.getRightBumper():
            self.pivotMotorOne.set(0.5)    
            self.pivotMotorTwo.set(0.5)    
            self.pivotOnePosition = self.pivotChannelOne.getPosition()
            self.pivotTwoPosition = self.pivotChannelTwo.getPosition()
        elif self.controller.getLeftBumper():
            self.pivotMotorOne.set(0.01)
            self.pivotMotorTwo.set(0.01)
            self.pivotOnePosition = self.pivotChannelOne.getPosition()
            self.pivotTwoPosition = self.pivotChannelTwo.getPosition()
        else:
            self.pivotPIDControllerOne.setReference(self.pivotOnePosition, rev.CANSparkMax.ControlType.kPosition)
            self.pivotPIDControllerTwo.setReference(self.pivotTwoPosition, rev.CANSparkMax.ControlType.kPosition)
