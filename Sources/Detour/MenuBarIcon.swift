import AppKit

/// Menu bar template images: the headphones symbol, with a small badge cut into its bottom-right
/// corner (1.4 pt clear gap) while waiting or warning, and headphones.slash when off.
enum MenuBarIcon {
    static func image(for status: Forwarder.Status) -> NSImage {
        switch status {
        case .sending: symbol("headphones")
        case .waitingForApp, .waitingForOutput: badged("clock.fill")
        case .appOnHeadphones, .needsPermission, .failed: badged("exclamationmark.circle.fill")
        case .off: symbol("headphones.slash")
        }
    }

    private static let config = NSImage.SymbolConfiguration(pointSize: 15, weight: .regular, scale: .medium)

    private static func symbol(_ name: String) -> NSImage {
        let image = NSImage(systemSymbolName: name, accessibilityDescription: "Detour")!
            .withSymbolConfiguration(config)!
        image.isTemplate = true
        return image
    }

    private static func badged(_ badge: String) -> NSImage {
        let base = symbol("headphones")
        let mark = NSImage(systemSymbolName: badge, accessibilityDescription: nil)!
            .withSymbolConfiguration(.init(pointSize: 8, weight: .bold))!
        let size = NSSize(width: base.size.width + 3, height: base.size.height)
        let badgeRect = NSRect(x: size.width - mark.size.width, y: 0, width: mark.size.width, height: mark.size.height)
        let image = NSImage(size: size, flipped: false) { _ in
            base.draw(in: NSRect(origin: .zero, size: base.size))
            NSGraphicsContext.current?.compositingOperation = .destinationOut
            NSBezierPath(ovalIn: badgeRect.insetBy(dx: -1.4, dy: -1.4)).fill()
            NSGraphicsContext.current?.compositingOperation = .sourceOver
            mark.draw(in: badgeRect)
            return true
        }
        image.isTemplate = true
        image.accessibilityDescription = "Detour"
        return image
    }
}
