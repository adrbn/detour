import Testing
@testable import Detour

/// Source at 48 000 Hz in steady 512-frame blocks, headphones pulling 0.15 % slower and in
/// irregular bursts, as measured on AirPods Pro 2. The cushion must settle, with no underrun.
@Test func cushionSettlesWithBurstyReader() {
    let bridge = Bridge()
    bridge.reset(sourceRate: 48_000, destinationRate: 48_000)
    let block = [Float](repeating: 0.5, count: 512 * 2)
    var out = [Float](repeating: 0, count: 2048 * 2)
    var written = 0.0, read = 0.0
    var silentAfterStart = 0
    var bursts = [256, 1024, 512, 2048, 128, 512]
    for step in 0..<20_000 {  // ~200 s of audio
        block.withUnsafeBufferPointer { bridge.write($0.baseAddress!, frames: 512, stride: 2) }
        written += 512
        while read < written * 0.9985 - bridge.target {
            let frames = bursts[step % bursts.count]
            bursts.swapAt(step % bursts.count, (step * 7) % bursts.count)
            out.withUnsafeMutableBufferPointer { bridge.read(into: $0.baseAddress!, frames: frames, stride: 2) }
            if step > 1_000, out[(frames - 1) * 2] == 0 { silentAfterStart += 1 }
            read += Double(frames)
        }
    }
    #expect(silentAfterStart == 0)
    #expect(abs(bridge.fill - bridge.target) < bridge.target)
    #expect(out[0] == 0.5)
}
