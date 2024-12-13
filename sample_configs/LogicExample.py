#!/usr/bin/python3

import PyApplicationCore as ac
import numpy
import time


class FindMax(ac.ApplicationModule):
    def __init__(self, owner):
        super().__init__(owner, "FindMax", "finds signal10 max position")

        self.signal = ac.ArrayPushInput(ac.DataType.int32, self, "/ADC/channels/signal10",
                                        "", 16384, "DAQ0 channel 10")
        self.maxPos = ac.ScalarOutput(
            ac.DataType.uint32, self, "maxPos", "", "")
        self.delay = ac.ScalarPollInput(ac.DataType.float32, self, "delay",
                                        "sec", "additional delay between reads")

    def mainLoop(self):
        # device is already initialized and current input values loaded
        print("FindMax mainLoop started")
        while True:

            self.maxPos.set(numpy.argmax(self.signal))
            self.writeAll()
            time.sleep(self.delay.get())

            self.readAll()


class NaiveEvaluation(ac.ApplicationModule):
    def __init__(self, owner):
        super().__init__(owner, "NaiveEvaluation", "demonstrates naive data matching")

        self.signal = ac.ArrayPushInput(
            ac.DataType.int32, self, "/ADC/channels/signal10", "", 16384, "DAQ0 channel 10")
        self.maxPos = ac.ScalarPushInput(
            ac.DataType.uint32, self, "../FindMax/maxPos", "", "")
        self.maxVal = ac.ScalarOutput(
            ac.DataType.int32, self, "maxVal", "", "")

        self.consistentSamples = ac.ScalarOutput(
            ac.DataType.uint32, self, "consistentSamplesA", "", "")
        self.inconsistentSamples = ac.ScalarOutput(
            ac.DataType.uint32, self, "inconsistentSamplesA", "", "")

    def mainLoop(self):
        while True:
            self.maxVal.set(self.signal[self.maxPos])
            maxValExpected = numpy.max(self.signal)
            if self.maxVal == maxValExpected:
                self.consistentSamples.set(self.consistentSamples + 1)
            else:
                self.inconsistentSamples.set(self.inconsistentSamples + 1)
            self.writeAll()
            self.readAll()


class ConsistentEvaluation(ac.ApplicationModule):
    def __init__(self, owner):
        super().__init__(owner, "ConsistentEvaluation",
                         "demonstrates consistent data matching")

        self.signal = ac.ArrayPushInput(
            ac.DataType.int32, self, "/ADC/channels/signal10", "", 16384, "DAQ0 channel 10")
        self.maxPos = ac.ScalarPushInput(
            ac.DataType.uint32, self, "../FindMax/maxPos", "", "")
        self.maxVal = ac.ScalarOutput(
            ac.DataType.int32, self, "maxVal", "", "")

        self.consistentSamples = ac.ScalarOutput(
            ac.DataType.uint32, self, "consistentSamplesB", "", "")
        self.inconsistentSamples = ac.ScalarOutput(
            ac.DataType.uint32, self, "inconsistentSamplesB", "", "")

    def mainLoop(self):
        rag = self.readAnyGroup()
        dcg = ac.DataConsistencyGroup(self.signal, self.maxPos)

        while True:
            elementId = rag.readAny()
            if dcg.update(elementId):
                # here we can process a consistent data set
                self.maxVal.set(self.signal[self.maxPos])
                maxValExpected = numpy.max(self.signal)
                if self.maxVal == maxValExpected:
                    self.consistentSamples.set(self.consistentSamples + 1)
                else:
                    self.inconsistentSamples.set(self.inconsistentSamples + 1)

                self.writeAll()


# instantiate user-defined application modules and reference them somehow from ac.app so they don't get deleted
# owner = ac.app means the module is mounted at the root of the process variable household.
# Differently from usual python semantics, the owner will manage lifetime of its owned elements.
ac.app.module1 = FindMax(ac.app)
ac.app.module2 = NaiveEvaluation(ac.app)
ac.app.module2a = ConsistentEvaluation(ac.app)
