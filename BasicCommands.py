"""
BotCommands provides another layer of abstraction between GameInputter and a Tekken Bot, allowing button presses to be
grouped together into larger building blocks like 'backdash' or 'do a combo' or 'block low'. In addition to button
presses, BotCommands accomadtes low level concepts in addition to buttons, like 'hit confirm' (check to see if this
combo isn't hitting) or 'pause until my next move comes out'.

A botcommand 'command' consists of a list of tuples, each one with a command and the amount of time to wait in frames before
performing it. UniversalCommands contains a few general sequences. They are also simple enough to be constructed on the fly
or read from a file.
"""

import random
from ButtonCommandEnum import Command
from TekkenGameState import TekkenGameState

class UniversalCommands:
    BACKDASH = list(zip(
        [Command.TapDown, Command.TapBack, Command.HoldBack, Command.ReleaseBack],
        [0, 0, 2, 12]
    ))

    FORWARDDASH_HALF = list(zip(
        [Command.TapForward, Command.TapForward, Command.TapBack],
        [0, 2, 5]
    ))

    SIDESTEP_RIGHT = list(zip(
        [Command.TapRight, Command.TapBack],
        [0, 4]
    ))

    SIDESTEP_LEFT = list(zip(
        [Command.TapLeft, Command.TapBack],
        [0, 4]
    ))

    SIDESTEP_UP = list(zip(
        [Command.TapUp, Command.TapBack],
        [0, 16]
    ))

    BLOCK_LONG = list(zip(
        [Command.HoldBack, Command.ReleaseBack, Command.Wait],
        [0, 20, 1]
    ))

    BLOCK_MID_FULL = list(zip(
        [Command.HoldBack, Command.ReleaseBack, Command.Wait],
        [0, 120, 1]
    ))

    BLOCK_LOW_FULL = list(zip(
        [Command.HoldDownBack, Command.ReleaseDownBack, Command.Wait],
        [0, 120, 1]
    ))

    LOW_PARRY = list(zip(
        [Command.HoldForward, Command.HoldDown, Command.ReleaseForward, Command.ReleaseDown],
        [0, 0, 120, 0]
    ))

    THROW_TECH_1 = list(zip(
        [Command.Tap1, Command.Tap1, Command.Tap1, Command.Tap1, Command.Tap1, Command.Tap1],
        [4, 4, 4, 4, 4, 4]
    ))

    THROW_TECH_12 = list(zip(
        [Command.Tap1, Command.Tap2, Command.Tap1, Command.Tap2, Command.Tap1, Command.Tap2, Command.Tap1, Command.Tap2, Command.Tap1, Command.Tap2, Command.Tap1, Command.Tap2],
        [4, 0, 4, 0, 4, 0, 4, 0, 4, 0, 4, 0]
    ))

    THROW_TECH_2 = list(zip(
        [Command.Tap2, Command.Tap2, Command.Tap2, Command.Tap2, Command.Tap2, Command.Tap2],
        [4, 4, 4, 4, 4, 4]
    ))

    MASH_CONTINUE = list(zip(
        [Command.Accept, Command.Accept],
        [4, 4]
    ))

class BotCommands:
    def __init__(self, inputController):
        self.updateFrame = 0
        self.isBusy = False
        self.inputController = inputController
        self.commandBuffer = []
        self.commandIndex = 0

    def Update(self, gameState):
        if self.updateFrame > 120:
            self.ClearCommands()

        if gameState.DidBotJustTakeDamage():
            self.ClearCommands()

        if not self.IsAvailable():
            if self.updateFrame == self.commandBuffer[self.commandIndex][1]:
                command = self.commandBuffer[self.commandIndex][0]
                self.commandIndex += 1
                self.ProcessCommand(command, gameState)
                self.updateFrame = 0
                self.Update(gameState)
            else:
                self.updateFrame += 1
        #print(self.updateFrame)



    def IsAvailable(self):
        return self.commandIndex >= len(self.commandBuffer)

    def GetUp(self):
        self.AddCommand([(Command.TapBack, 1)])

    def MashTech(self):
        if random.randint(0, 1) == 0:
            self.AddCommand(UniversalCommands.THROW_TECH_1)
        else:
            self.AddCommand(UniversalCommands.THROW_TECH_2)

    def Backdash(self):
        self.AddCommand(UniversalCommands.BACKDASH)

    def ForwarddashSmall(self):
        self.AddCommand(UniversalCommands.FORWARDDASH_HALF)

    def SidestepRight(self):
        self.AddCommand(UniversalCommands.SIDESTEP_RIGHT)

    def SidestepLeft(self):
        self.AddCommand(UniversalCommands.SIDESTEP_LEFT)

    def SidestepUp(self):
        self.AddCommand(UniversalCommands.SIDESTEP_UP)

    def BlockAndWait(self):
        self.AddCommand(UniversalCommands.BLOCK_LONG)

    def ThrowTech(self):
        self.AddCommand(UniversalCommands.THROW_TECH_1)

    def BlockMidFull(self, startup):
        self.commandBuffer = []
        self.AddCommand(UniversalCommands.BLOCK_MID_FULL)
        self.commandBuffer[1] = (self.commandBuffer[1][0], startup)

    def BlockLowFull(self, startup):
        self.commandBuffer = []
        self.AddCommand(UniversalCommands.BLOCK_LOW_FULL)
        self.commandBuffer[1] = (self.commandBuffer[1][0], startup)

    def LowParry(self, startup):
        self.commandBuffer = []
        self.AddCommand(UniversalCommands.LOW_PARRY)
        self.commandBuffer[2] = (self.commandBuffer[2][0], startup)

    def WalkForward(self, startup):
        self.commandBuffer = []
        self.AddCommand([(Command.HoldForward, startup)])

    def MashContinue(self):
        self.AddCommand(UniversalCommands.MASH_CONTINUE)

    def AddCommand(self, buffer):
        if self.IsAvailable():
            self.commandBuffer = list(buffer)
            self.updateFrame = 0
            self.commandIndex = 0

    def ProcessCommand(self, command, gameState:TekkenGameState):
        #print(command)
        if command == Command.TapForward:
            self.inputController.TapForward()
        if command == Command.TapBack:
            self.inputController.TapBack()
        if command == Command.TapUp:
            self.inputController.TapUp()
        if command == Command.TapDown:
            self.inputController.TapDown()
        if command == Command.TapRight:
            self.inputController.TapRight()
        if command == Command.TapLeft:
            self.inputController.TapLeft()
        if command == Command.Tap1:
            self.inputController.Tap1()
        if command == Command.Tap2:
            self.inputController.Tap2()
        if command == Command.Tap3:
            self.inputController.Tap3()
        if command == Command.Tap4:
            self.inputController.Tap4()
        if command == Command.Accept:
            self.inputController.TapAccept()
        if command == Command.HoldBack:
            self.inputController.HoldBack()
        if command == Command.ReleaseBack:
            self.inputController.TapBack()
        if command == Command.HoldForward:
            self.inputController.HoldForward()
        if command == Command.ReleaseForward:
            self.inputController.ReleaseForward()
        if command == Command.HoldDown:
            self.inputController.HoldDown()
        if command == Command.ReleaseDown:
            self.inputController.ReleaseDown()
        if command == Command.HoldUp:
            self.inputController.HoldUp()
        if command == Command.ReleaseUp:
            self.inputController.ReleaseUp()
        if command == Command.HoldDownBack:
            self.inputController.HoldBack()
            self.inputController.HoldDown()
        if command == Command.ReleaseDownBack:
            self.inputController.ReleaseBack()
            self.inputController.ReleaseDown()

        if command == Command.ReleaseAll:
            self.inputController.Release()


        if command == Command.PunishConfirm:
            if gameState.DidBotRecentlyDoMove():
                pass
            else:
                self.commandIndex = 0

        if command == Command.HitConfirm:
            if gameState.DidBotRecentlyDoDamage:
                pass
            else:
                self.ClearCommands()

        if command == Command.Nextmove:
            if gameState.IsBotMoveChanged() or gameState.IsBotAttackStarting():
                #print(gameState.GetBotJustMoveID())
                #print(gameState.stateLog[-1].bot.move_id)
                pass
            else:
                self.commandIndex -= 1
                self.commandBuffer[self.commandIndex] = (Command.Nextmove, 1)

        if command == Command.Startupmove:
            self.commandIndex -= 1
            #print(gameState.GetBotTimeUntilImpact())
            self.commandBuffer[self.commandIndex] = (Command.Wait, gameState.GetBotTimeUntilImpact() * -1)


        if command == Command.Recovery:
            self.commandIndex -= 1
            inputDelay = 0
            self.commandBuffer[self.commandIndex] = (Command.Wait, max(0, gameState.GetBotFramesUntilRecoveryEnds() - 6 - inputDelay))

        if command == Command.FullRecovery:

            if gameState.GetBotRecovery() - gameState.GetBotMoveTimer() < 6:
                pass
            else:
                self.commandIndex -= 1
                self.commandBuffer[self.commandIndex] = (Command.FullRecovery, 1)


    def ClearCommands(self):
        self.commandBuffer = []
        self.inputController.Release()
        self.updateFrame = 0
