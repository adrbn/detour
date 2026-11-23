import CoreAudio
import Foundation

/// Thin read-only helpers over the Core Audio HAL property API.
enum HAL {
    static let system = AudioObjectID(kAudioObjectSystemObject)

    static func address(_ selector: AudioObjectPropertySelector,
                        _ scope: AudioObjectPropertyScope = kAudioObjectPropertyScopeGlobal) -> AudioObjectPropertyAddress {
        AudioObjectPropertyAddress(mSelector: selector, mScope: scope, mElement: kAudioObjectPropertyElementMain)
    }

    static func ids(_ object: AudioObjectID, _ selector: AudioObjectPropertySelector,
                    _ scope: AudioObjectPropertyScope = kAudioObjectPropertyScopeGlobal) -> [AudioObjectID] {
        var addr = address(selector, scope)
        var size: UInt32 = 0
        guard AudioObjectGetPropertyDataSize(object, &addr, 0, nil, &size) == noErr, size > 0 else { return [] }
        var result = [AudioObjectID](repeating: 0, count: Int(size) / MemoryLayout<AudioObjectID>.size)
        guard AudioObjectGetPropertyData(object, &addr, 0, nil, &size, &result) == noErr else { return [] }
        return result
    }

    static func string(_ object: AudioObjectID, _ selector: AudioObjectPropertySelector) -> String? {
        var addr = address(selector)
        var value: Unmanaged<CFString>?
        var size = UInt32(MemoryLayout<Unmanaged<CFString>?>.size)
        guard AudioObjectGetPropertyData(object, &addr, 0, nil, &size, &value) == noErr else { return nil }
        return value?.takeRetainedValue() as String?
    }

    static func uint32(_ object: AudioObjectID, _ selector: AudioObjectPropertySelector,
                       _ scope: AudioObjectPropertyScope = kAudioObjectPropertyScopeGlobal) -> UInt32 {
        var addr = address(selector, scope)
        var value: UInt32 = 0
        var size = UInt32(MemoryLayout<UInt32>.size)
        AudioObjectGetPropertyData(object, &addr, 0, nil, &size, &value)
        return value
    }

    static func double(_ object: AudioObjectID, _ selector: AudioObjectPropertySelector) -> Double {
        var addr = address(selector)
        var value: Float64 = 0
        var size = UInt32(MemoryLayout<Float64>.size)
        AudioObjectGetPropertyData(object, &addr, 0, nil, &size, &value)
        return value
    }

    static func hasOutput(_ device: AudioObjectID) -> Bool {
        !ids(device, kAudioDevicePropertyStreams, kAudioObjectPropertyScopeOutput).isEmpty
    }
}

/// An output device as the menu shows it.
struct OutputDevice: Equatable, Identifiable {
    let id: AudioObjectID
    let uid: String
    let name: String
    let isBluetooth: Bool
    var isBuiltIn = false

    static func all() -> [OutputDevice] {
        HAL.ids(HAL.system, kAudioHardwarePropertyDevices).compactMap { id in
            guard HAL.hasOutput(id),
                  let uid = HAL.string(id, kAudioDevicePropertyDeviceUID),
                  let name = HAL.string(id, kAudioObjectPropertyName),
                  !uid.hasPrefix("detour.") else { return nil }
            let transport = HAL.uint32(id, kAudioDevicePropertyTransportType)
            return OutputDevice(id: id, uid: uid, name: name,
                                isBluetooth: transport == kAudioDeviceTransportTypeBluetooth
                                    || transport == kAudioDeviceTransportTypeBluetoothLE,
                                isBuiltIn: transport == kAudioDeviceTransportTypeBuiltIn)
        }
    }

    /// The saved device if it is connected; with no saved choice, the first Bluetooth output.
    /// A saved device that is absent yields nil: we wait for it rather than play somewhere else.
    static func pick(from devices: [OutputDevice], preferredUID: String?) -> OutputDevice? {
        if let preferredUID, !preferredUID.isEmpty {
            return devices.first { $0.uid == preferredUID }
        }
        return devices.first { $0.isBluetooth }
    }
}

/// A process that currently has an audio client, as Core Audio sees it.
struct AudioProcess: Equatable, Identifiable {
    let id: AudioObjectID
    let pid: pid_t
    let bundleID: String

    static func all() -> [AudioProcess] {
        HAL.ids(HAL.system, kAudioHardwarePropertyProcessObjectList).compactMap { id in
            guard let bundleID = HAL.string(id, kAudioProcessPropertyBundleID), !bundleID.isEmpty else { return nil }
            let pid = pid_t(bitPattern: HAL.uint32(id, kAudioProcessPropertyPID))
            return AudioProcess(id: id, pid: pid, bundleID: bundleID)
        }
    }
}
