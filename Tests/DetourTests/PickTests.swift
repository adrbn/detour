import Testing
@testable import Detour

private let speakers = OutputDevice(id: 1, uid: "BuiltIn", name: "MacBook Speakers", isBluetooth: false)
private let airpods = OutputDevice(id: 2, uid: "AA-BB", name: "AirPods Pro", isBluetooth: true)

@Test func noChoicePicksFirstBluetooth() {
    #expect(OutputDevice.pick(from: [speakers, airpods], preferredUID: "") == airpods)
    #expect(OutputDevice.pick(from: [speakers, airpods], preferredUID: nil) == airpods)
}

@Test func savedChoiceWins() {
    #expect(OutputDevice.pick(from: [speakers, airpods], preferredUID: "BuiltIn") == speakers)
}

/// AirPods out of the ears: the saved device is gone, so wait instead of playing elsewhere.
@Test func absentDeviceMeansWait() {
    #expect(OutputDevice.pick(from: [speakers], preferredUID: "AA-BB") == nil)
    #expect(OutputDevice.pick(from: [speakers], preferredUID: "") == nil)
}
