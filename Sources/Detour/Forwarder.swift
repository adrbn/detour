import CoreAudio
import Foundation
import os

/// Sends one app's audio to an output device the app itself never opens.
///
/// Why: a DAW pointed at AirPods sees their ~160 ms of Bluetooth latency and, in FL Studio
/// at least, renders crackly, off-pitch audio. Left on the Mac speakers it renders cleanly;
/// we mute it there with a process tap and replay the tap on the headphones.
///
/// The tap is read on the speakers' steady clock and handed to the headphones through `Bridge`:
/// AirPods consume audio irregularly, and anything slaved to their clock crackles.
///
/// AirPods vanish from Core Audio when taken out of the ears and come back when put in,
/// so the playback side is rebuilt by `reconcile()`, which runs every half second.
@MainActor
final class Forwarder: ObservableObject {
    enum Status: Equatable {
        case off
        case waitingForApp
        case waitingForOutput
        case sending(String)
        /// The app itself plays on the headphones (FL's "Default audio device" follows the
        /// system output there), so it renders the broken audio we are trying to avoid.
        case appOnHeadphones(String)
        case failed(String)
    }

    @Published private(set) var status: Status = .off
    @Published private(set) var processes: [AudioProcess] = []
    @Published private(set) var outputs: [OutputDevice] = []

    var enabled = false { didSet { reconcile() } }
    var appBundleID = "" { didSet { if oldValue != appBundleID { teardown(); reconcile() } } }
    var outputUID = "" { didSet { if oldValue != outputUID { teardownRoute(); reconcile() } } }

    private let log = Logger(subsystem: "detour", category: "forwarder")
    private var timer: Timer?

    // The tap mutes the app for as long as it exists, which is also what keeps the speakers
    // quiet while the headphones are out of the ears.
    private var tap: AudioObjectID = 0
    private var tapUUID = ""
    private var tappedProcess: AudioObjectID = 0

    // Capture: a private aggregate of the Mac speakers plus the tap, so the tap is read on the
    // steady speaker clock (FL renders there too). It feeds `bridge`.
    private var capture: AudioObjectID = 0
    private var captureProc: AudioDeviceIOProcID?
    private var captureRate = 0.0

    // Playback: an IOProc straight on the headphones, reading `bridge` at their own pace.
    private var playbackProc: AudioDeviceIOProcID?
    private var routedOutput: AudioObjectID = 0

    private let bridge = Bridge()

    static let defaultApp = "com.image-line.flstudio"

    init(defaults: UserDefaults = .standard) {
        defaults.register(defaults: ["enabled": true, "appBundleID": Self.defaultApp])
        enabled = defaults.bool(forKey: "enabled")
        appBundleID = defaults.string(forKey: "appBundleID") ?? Self.defaultApp
        outputUID = defaults.string(forKey: "outputUID") ?? ""
        timer = Timer.scheduledTimer(withTimeInterval: 0.5, repeats: true) { [weak self] _ in
            MainActor.assumeIsolated { self?.reconcile() }
        }
        reconcile()
    }

    func reconcile() {
        processes = AudioProcess.all()
        outputs = OutputDevice.all()

        guard enabled else { teardown(); status = .off; return }

        guard let process = processes.first(where: { $0.bundleID == appBundleID }) else {
            teardown(); status = .waitingForApp; return
        }
        if tap != 0, tappedProcess != process.id { teardown() }
        if tap == 0, !makeTap(for: process) { return }
        if capture == 0, !makeCapture() { return }

        guard let output = OutputDevice.pick(from: outputs, preferredUID: outputUID) else {
            teardownRoute(); status = .waitingForOutput; return
        }
        let routeAlive = playbackProc != nil && routedOutput == output.id
            && HAL.uint32(output.id, kAudioDevicePropertyDeviceIsAlive) != 0
        if !routeAlive {
            teardownRoute()
            guard makeRoute(to: output) else { return }
        }
        let appDevices = HAL.ids(process.id, kAudioProcessPropertyDevices, kAudioObjectPropertyScopeOutput)
        status = appDevices.contains(output.id) ? .appOnHeadphones(output.name) : .sending(output.name)
    }

    func shutdown() {
        timer?.invalidate()
        teardown()
    }

    // MARK: - Building

    private func makeTap(for process: AudioProcess) -> Bool {
        let description = CATapDescription(stereoMixdownOfProcesses: [process.id])
        description.isPrivate = true
        description.muteBehavior = .muted
        var newTap: AudioObjectID = 0
        let err = AudioHardwareCreateProcessTap(description, &newTap)
        guard err == noErr else {
            // Most often: the System Audio Recording permission was refused.
            fail("Could not capture the app (error \(err)). Allow Detour in System Settings › Privacy & Security › Screen & System Audio Recording.")
            return false
        }
        tap = newTap
        tapUUID = description.uuid.uuidString
        tappedProcess = process.id
        log.info("tapped \(process.bundleID, privacy: .public) pid \(process.pid)")
        return true
    }

    private func makeCapture() -> Bool {
        guard let speakers = OutputDevice.all().first(where: \.isBuiltIn) else {
            fail("No built-in output to clock the capture from."); return false
        }
        let description: [String: Any] = [
            kAudioAggregateDeviceNameKey: "Detour capture",
            kAudioAggregateDeviceUIDKey: "detour.\(UUID().uuidString)",
            kAudioAggregateDeviceIsPrivateKey: true,
            kAudioAggregateDeviceMainSubDeviceKey: speakers.uid,
            kAudioAggregateDeviceSubDeviceListKey: [[kAudioSubDeviceUIDKey: speakers.uid]],
            // Same clock as the app when it plays on the speakers; harmless otherwise.
            kAudioAggregateDeviceTapListKey: [[kAudioSubTapUIDKey: tapUUID, kAudioSubTapDriftCompensationKey: true]],
            kAudioAggregateDeviceTapAutoStartKey: true,
        ]
        var device: AudioObjectID = 0
        var err = AudioHardwareCreateAggregateDevice(description as CFDictionary, &device)
        guard err == noErr else { fail("Could not capture the app (error \(err))."); return false }

        let bridge = bridge
        var proc: AudioDeviceIOProcID?
        err = AudioDeviceCreateIOProcIDWithBlock(&proc, device, nil) { _, input, _, output, _ in
            let inputs = UnsafeMutableAudioBufferListPointer(UnsafeMutablePointer(mutating: input))
            if let buffer = inputs.first, let data = buffer.mData, buffer.mNumberChannels > 0 {
                let stride = Int(buffer.mNumberChannels)
                bridge.write(data.assumingMemoryBound(to: Float.self),
                             frames: Int(buffer.mDataByteSize) / 4 / stride, stride: stride)
            }
            for buffer in UnsafeMutableAudioBufferListPointer(output) {
                if let data = buffer.mData { memset(data, 0, Int(buffer.mDataByteSize)) }
            }
        }
        if err == noErr { err = AudioDeviceStart(device, proc) }
        guard err == noErr else {
            if let proc { AudioDeviceDestroyIOProcID(device, proc) }
            AudioHardwareDestroyAggregateDevice(device)
            fail("Could not start the capture (error \(err)).")
            return false
        }
        capture = device
        captureProc = proc
        captureRate = HAL.double(device, kAudioDevicePropertyNominalSampleRate)
        log.info("capturing on \(speakers.name, privacy: .public) at \(self.captureRate) Hz")
        return true
    }

    private func makeRoute(to output: OutputDevice) -> Bool {
        let outputRate = HAL.double(output.id, kAudioDevicePropertyNominalSampleRate)
        bridge.reset(sourceRate: captureRate, destinationRate: outputRate)
        let bridge = bridge
        var proc: AudioDeviceIOProcID?
        var err = AudioDeviceCreateIOProcIDWithBlock(&proc, output.id, nil) { _, _, _, output, _ in
            for (index, buffer) in UnsafeMutableAudioBufferListPointer(output).enumerated() {
                guard let data = buffer.mData else { continue }
                let stride = Int(buffer.mNumberChannels)
                if index == 0, stride > 0 {
                    bridge.read(into: data.assumingMemoryBound(to: Float.self),
                                frames: Int(buffer.mDataByteSize) / 4 / stride, stride: stride)
                } else {
                    memset(data, 0, Int(buffer.mDataByteSize))
                }
            }
        }
        if err == noErr { err = AudioDeviceStart(output.id, proc) }
        guard err == noErr else {
            if let proc { AudioDeviceDestroyIOProcID(output.id, proc) }
            fail("Could not start playback on \(output.name) (error \(err)).")
            return false
        }
        playbackProc = proc
        routedOutput = output.id
        log.info("playing on \(output.name, privacy: .public) at \(outputRate) Hz")
        return true
    }

    // MARK: - Tearing down

    private func teardownRoute() {
        guard let playbackProc else { return }
        AudioDeviceStop(routedOutput, playbackProc)
        AudioDeviceDestroyIOProcID(routedOutput, playbackProc)
        self.playbackProc = nil
        routedOutput = 0
    }

    private func teardown() {
        teardownRoute()
        if capture != 0 {
            if let captureProc {
                AudioDeviceStop(capture, captureProc)
                AudioDeviceDestroyIOProcID(capture, captureProc)
            }
            AudioHardwareDestroyAggregateDevice(capture)
            capture = 0
            captureProc = nil
        }
        guard tap != 0 else { return }
        AudioHardwareDestroyProcessTap(tap)
        tap = 0
        tapUUID = ""
        tappedProcess = 0
    }

    private func fail(_ message: String) {
        log.error("\(message, privacy: .public)")
        teardown()
        status = .failed(message)
    }
}
