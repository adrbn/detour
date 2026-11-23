import AppKit
import SwiftUI

@main
struct DetourApp: App {
    @StateObject private var forwarder = Forwarder()
    // Same keys and defaults as Forwarder.init, which reads them at launch.
    @AppStorage("enabled") private var enabled = true
    @AppStorage("appBundleID") private var appBundleID = Forwarder.defaultApp
    @AppStorage("outputUID") private var outputUID = ""

    var body: some Scene {
        MenuBarExtra {
            Menu
        } label: {
            Image(systemName: icon)
        }
    }

    private var icon: String {
        switch forwarder.status {
        case .sending: "headphones"
        case .failed, .appOnHeadphones: "exclamationmark.triangle"
        default: "headphones.slash"  // off, or waiting for the app or the headphones
        }
    }

    @ViewBuilder private var Menu: some View {
        Text(statusLine)
        Divider()
        Toggle("Send to headphones", isOn: $enabled)
            .onChange(of: enabled) { _, value in forwarder.enabled = value }

        Picker("App", selection: $appBundleID) {
            ForEach(appChoices, id: \.self) { Text(appName($0)).tag($0) }
        }
        .onChange(of: appBundleID) { _, value in forwarder.appBundleID = value }

        Picker("Output", selection: $outputUID) {
            Text("First Bluetooth device").tag("")
            ForEach(forwarder.outputs) { Text($0.name).tag($0.uid) }
        }
        .onChange(of: outputUID) { _, value in forwarder.outputUID = value }

        Divider()
        Text("Keep the app's own output on the Mac speakers.")
        Button("Quit Detour") {
            forwarder.shutdown()
            NSApp.terminate(nil)
        }
        .keyboardShortcut("q")
    }

    private var statusLine: String {
        switch forwarder.status {
        case .off: "Off"
        case .waitingForApp: "Waiting for \(appName(appBundleID)) to play audio"
        case .waitingForOutput: "Waiting for the headphones"
        case .sending(let device): "\(appName(appBundleID)) → \(device)"
        case .appOnHeadphones(let device): "\(appName(appBundleID)) plays on \(device) itself: set its output to the Mac speakers"
        case .failed(let message): message
        }
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
