import AppKit
import SwiftUI

/// `Detour --render-states <folder>`: shows the real menu view in every state, light and dark,
/// in windows hidden behind the desktop, for scripts/readme-shots.sh to capture.
/// Add `-AppleAccentColor 4` to draw with the default blue accent. Never touches the user's settings.
@MainActor
enum Snapshots {
    static let states: [(String, Forwarder.Status, app: String)] = [
        ("sending", .sending("AirPods Pro 2"), Forwarder.defaultApp),
        ("waiting-app", .waitingForApp, Forwarder.defaultApp),
        ("waiting-headphones", .waitingForOutput, Forwarder.defaultApp),
        ("app-on-headphones", .appOnHeadphones("AirPods Pro 2"), Forwarder.defaultApp),
        ("permission", .needsPermission, Forwarder.defaultApp),
        ("off", .off, Forwarder.defaultApp),
        ("sending-music", .sending("AirPods Pro 2"), "com.apple.Music"),
        ("sending-safari", .sending("AirPods Pro 2"), "com.apple.Safari"),
    ]

    /// The folder given after `--render-states`, if any.
    static var folder: URL? {
        let args = CommandLine.arguments
        guard let i = args.firstIndex(of: "--render-states"), i + 1 < args.count else { return nil }
        return URL(fileURLWithPath: args[i + 1])
    }

    /// Opens one window per state and appearance and lists them in `windows.txt`
    /// ("name windowNumber" per line). The app quits by itself after 8 s.
    static func render(to folder: URL) {
        try? FileManager.default.createDirectory(at: folder, withIntermediateDirectories: true)
        var lines: [String] = []
        for (name, status, app) in states {
            for (suffix, appearance) in [("light", NSAppearance.Name.aqua), ("dark", .darkAqua)] {
                // One throwaway defaults suite per state, so the user's own settings are never read or written.
                let store = UserDefaults(suiteName: "detour.snapshots.\(name)")!
                store.set(status != .off, forKey: "enabled")
                store.set(app, forKey: "appBundleID")
                store.set("", forKey: "outputUID")
                let view = DetourView(forwarder: Forwarder(previewing: status))
                    .defaultAppStorage(store)
                    .background(Color(nsColor: .windowBackgroundColor))
                let window = open(view, appearance: appearance, index: windows.count)
                windows.append(window)
                lines.append("\(name)-\(suffix) \(window.windowNumber)")
            }
        }
        try? (lines.joined(separator: "\n") + "\n").write(to: folder.appendingPathComponent("windows.txt"),
                                                         atomically: true, encoding: .utf8)
        DispatchQueue.main.asyncAfter(deadline: .now() + 8) { exit(0) }
    }

    private static var windows: [NSWindow] = []

    private static func open(_ view: some View, appearance: NSAppearance.Name, index: Int) -> NSWindow {
        let host = NSHostingView(rootView: view)
        host.frame.size = host.fittingSize
        let window = FocusedLookingPanel(contentRect: host.frame, styleMask: [.borderless, .nonactivatingPanel],
                                         backing: .buffered, defer: false)
        window.appearance = NSAppearance(named: appearance)
        window.contentView = host
        window.hasShadow = false
        // On screen (screencapture needs that) but behind the desktop picture, so nobody sees it.
        window.level = NSWindow.Level(rawValue: Int(CGWindowLevelForKey(.desktopWindow)) - 1)
        window.setFrameOrigin(NSPoint(x: 40 + 20 * index, y: 40))
        window.orderFrontRegardless()
        return window
    }
}

/// Draws its controls as in the focused window of the active app (blue switch, blue button)
/// without taking focus: macOS won't activate a process started from a script.
/// The underscored methods are AppKit's own checks; this class only exists for the README captures.
private final class FocusedLookingPanel: NSPanel {
    override var isKeyWindow: Bool { true }
    override var isMainWindow: Bool { true }
    @objc func _hasActiveAppearance() -> Bool { true }
    @objc func _hasActiveAppearanceIgnoringKeyFocus() -> Bool { true }
    @objc func _hasKeyAppearance() -> Bool { true }
    @objc func _hasMainAppearance() -> Bool { true }
}
