// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "Detour",
    // Process taps (CATapDescription) arrived in macOS 14.2.
    platforms: [.macOS("14.2")],
    targets: [
        .executableTarget(name: "Detour", path: "Sources/Detour"),
        .testTarget(name: "DetourTests", dependencies: ["Detour"], path: "Tests/DetourTests"),
    ]
)
