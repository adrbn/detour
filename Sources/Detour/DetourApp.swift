import AppKit
import SwiftUI

@main
struct DetourApp: App {
    @StateObject private var forwarder: Forwarder

    init() {
        if let folder = Snapshots.folder {
            // README captures: a forwarder that does nothing, so no audio is touched meanwhile.
            _forwarder = StateObject(wrappedValue: Forwarder(previewing: .off))
            DispatchQueue.main.async { Snapshots.render(to: folder) }
        } else {
            _forwarder = StateObject(wrappedValue: Forwarder())
        }
    }

    var body: some Scene {
        MenuBarExtra {
            DetourView(forwarder: forwarder)
        } label: {
            Image(nsImage: MenuBarIcon.image(for: forwarder.status))
        }
        .menuBarExtraStyle(.window)
    }
}

/// The popover: switch, one status row, the two pickers, Quit. 300 pt wide, height hugs content.
struct DetourView: View {
    @ObservedObject var forwarder: Forwarder
    // Same keys and defaults as Forwarder.init, which reads them at launch.
    @AppStorage("enabled") private var enabled = true
    @AppStorage("appBundleID") private var appBundleID = Forwarder.defaultApp
    @AppStorage("outputUID") private var outputUID = ""
    @Environment(\.openURL) private var openURL

    var body: some View {
        VStack(spacing: 0) {
            HStack {
                Text("Send to headphones").font(.headline)
                Spacer()
                Toggle("Send to headphones", isOn: $enabled)
                    .toggleStyle(.switch).labelsHidden().controlSize(.small)
                    .onChange(of: enabled) { _, value in forwarder.enabled = value }
            }
            .padding(.horizontal, 16).padding(.top, 14).padding(.bottom, 10)

            Divider().padding(.horizontal, 16)
            status.padding(.horizontal, 16).padding(.vertical, 12)
            Divider().padding(.horizontal, 16)

            VStack(spacing: 8) {
                row("App") {
                    Picker("App", selection: $appBundleID) {
                        ForEach(appChoices, id: \.self) { Text(appName($0)).tag($0) }
                    }
                    .onChange(of: appBundleID) { _, value in forwarder.appBundleID = value }
                }
                row("Output") {
                    Picker("Output", selection: $outputUID) {
                        Text("First Bluetooth device").tag("")
                        Divider()
                        ForEach(forwarder.outputs) { Text($0.name).tag($0.uid) }
                    }
                    .onChange(of: outputUID) { _, value in forwarder.outputUID = value }
                }
            }
            .padding(.horizontal, 16).padding(.vertical, 12)

            Divider().padding(.horizontal, 16)
            HStack {
                Button("Quit Detour") {
                    forwarder.shutdown()
                    NSApp.terminate(nil)
                }
                .buttonStyle(.plain).keyboardShortcut("q")
                Spacer()
                Text("⌘Q").foregroundStyle(.tertiary)
            }
            .foregroundStyle(.secondary)
            .padding(.horizontal, 16).padding(.top, 10).padding(.bottom, 12)
        }
        .frame(width: 300)
    }

    /// A label on the left, a menu picker hugging its content on the right.
    private func row(_ label: String, @ViewBuilder picker: () -> some View) -> some View {
        HStack(spacing: 12) {
            Text(label)
            Spacer(minLength: 0)
            picker().pickerStyle(.menu).labelsHidden().fixedSize()
        }
    }

    private var status: some View {
        let s = StatusText(forwarder.status, app: appName(appBundleID), device: deviceName)
        return HStack(alignment: .top, spacing: 10) {
            Image(systemName: s.symbol)
                .font(.system(size: 13, weight: .semibold))
                .foregroundStyle(s.symbolStyle)
                .symbolEffect(.pulse, isActive: s.pulses)
                .frame(width: 28, height: 28)
                .background(Circle().fill(s.isSending ? AnyShapeStyle(.tint) : AnyShapeStyle(.quaternary)))
            VStack(alignment: .leading, spacing: 2) {
                Text(s.title).font(.body.weight(.semibold))
                Text(s.sentence).font(.callout).foregroundStyle(.secondary)
                    .fixedSize(horizontal: false, vertical: true)
                if s.needsSettings {
                    Button("Open System Settings") {
                        openURL(URL(string: "x-apple.systempreferences:com.apple.preference.security?Privacy_AudioCapture")!)
                    }
                    .buttonStyle(.borderedProminent).controlSize(.regular).padding(.top, 6)
                }
            }
            Spacer(minLength: 0)
        }
    }

    /// The chosen device's name, or "headphones" while it is "First Bluetooth device" and none is connected.
    private var deviceName: String {
        if case .sending(let name) = forwarder.status { return name }
        if case .appOnHeadphones(let name) = forwarder.status { return name }
        if !outputUID.isEmpty, let device = forwarder.outputs.first(where: { $0.uid == outputUID }) { return device.name }
        return "headphones"
    }

    /// Apps that currently have audio, plus the saved one even when it is not running.
    private var appChoices: [String] {
        let running = forwarder.processes.map(\.bundleID).filter { $0 != Bundle.main.bundleIdentifier }
        return Array(Set(running + [appBundleID])).sorted { appName($0) < appName($1) }
    }

    private func appName(_ bundleID: String) -> String {
        if let app = NSRunningApplication.runningApplications(withBundleIdentifier: bundleID).first,
           let name = app.localizedName { return name }
        if let url = NSWorkspace.shared.urlForApplication(withBundleIdentifier: bundleID) {
            return FileManager.default.displayName(atPath: url.path).replacingOccurrences(of: ".app", with: "")
        }
        return bundleID
    }
}

/// What the status row says for each state, from the Claude Design spec.
struct StatusText {
    var symbol: String
    var title: String
    var sentence: String
    var isSending = false
    var pulses = false
    var warns = false
    var needsSettings = false

    var symbolStyle: AnyShapeStyle {
        if isSending { return AnyShapeStyle(.white) }
        if warns { return AnyShapeStyle(.orange) }
        return AnyShapeStyle(.secondary)
    }

    init(_ status: Forwarder.Status, app: String, device: String) {
        switch status {
        case .sending:
            self.init(symbol: "headphones", title: "\(app) → \(device)",
                      sentence: "Your speakers are muted and the sound plays in your headphones.", isSending: true)
        case .waitingForApp:
            self.init(symbol: "waveform", title: "Waiting for \(app)",
                      sentence: "Press play in \(app) and the sound will follow.", pulses: true)
        case .waitingForOutput:
            self.init(symbol: "headphones", title: "Waiting for \(device)",
                      sentence: "The speakers stay silent, and the sound comes back on its own when you put them in.", pulses: true)
        case .appOnHeadphones:
            self.init(symbol: "exclamationmark.triangle.fill", title: "\(app) is playing on your \(device)",
                      sentence: "In \(app), open Options › Audio settings and set Output to Mac speakers.", warns: true)
        case .needsPermission:
            self.init(symbol: "lock.fill", title: "Detour needs permission",
                      sentence: "Allow System Audio Recording so Detour can hear \(app).", needsSettings: true)
        case .failed(let message):
            self.init(symbol: "exclamationmark.triangle.fill", title: "Something went wrong", sentence: message, warns: true)
        case .off:
            self.init(symbol: "speaker.wave.2", title: "Detour is off", sentence: "\(app) plays on your Mac speakers as usual.")
        }
    }

    private init(symbol: String, title: String, sentence: String, isSending: Bool = false,
                 pulses: Bool = false, warns: Bool = false, needsSettings: Bool = false) {
        self.symbol = symbol; self.title = title; self.sentence = sentence
        self.isSending = isSending; self.pulses = pulses; self.warns = warns; self.needsSettings = needsSettings
    }
}
