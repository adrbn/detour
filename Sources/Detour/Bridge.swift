import Foundation
import os

/// Carries stereo audio from one device clock to another.
///
/// Bluetooth headphones pull audio in irregular bursts (we measured 48 128 to 50 688 frames in
/// consecutive seconds on AirPods Pro 2). Locking the source to that clock, which is what an
/// aggregate device with drift compensation does, makes the pitch wobble and the sound crackle.
/// Instead the source writes at its own steady pace and the headphones read from a cushion,
/// with a resampling ratio that follows the cushion's fill level only very slowly.
final class Bridge: @unchecked Sendable {
    /// Fill level we steer towards: big enough to absorb a Bluetooth burst.
    let target: Double
    private let capacity: Int
    private var ring: [Float]   // interleaved stereo
    private var writeIndex = 0  // in frames, monotonic
    private var readPosition = 0.0  // in frames, fractional
    private var smoothedFill: Double
    private var baseRatio = 1.0  // source rate / destination rate
    private var primed = false
    // ponytail: an unfair lock shared by two realtime threads, held for a copy only. A lock-free
    // SPSC ring is the upgrade if glitches ever show up under load.
    private let lock = OSAllocatedUnfairLock()

    init(targetFrames: Int = 4_800, capacityFrames: Int = 48_000) {
        target = Double(targetFrames)
        capacity = capacityFrames
        ring = [Float](repeating: 0, count: capacityFrames * 2)
        smoothedFill = Double(targetFrames)
    }

    /// New destination: wait for a full cushion again before playing.
    func reset(sourceRate: Double, destinationRate: Double) {
        lock.lock(); defer { lock.unlock() }
        baseRatio = sourceRate > 0 && destinationRate > 0 ? sourceRate / destinationRate : 1
        readPosition = Double(writeIndex)
        smoothedFill = target
        primed = false
    }

    /// Source side. `stride` is the number of interleaved channels in `samples`.
    func write(_ samples: UnsafePointer<Float>, frames: Int, stride: Int) {
        lock.lock(); defer { lock.unlock() }
        for frame in 0..<frames {
            let slot = (writeIndex % capacity) * 2
            ring[slot] = samples[frame * stride]
            ring[slot + 1] = samples[frame * stride + (stride > 1 ? 1 : 0)]
            writeIndex += 1
        }
        // Nobody reading (headphones out of the ears): keep only a cushion's worth.
        if Double(writeIndex) - readPosition > Double(capacity - 1) {
            readPosition = Double(writeIndex) - target
        }
    }

    /// Destination side. Fills the first two of `stride` interleaved channels, zeroes the rest.
    func read(into out: UnsafeMutablePointer<Float>, frames: Int, stride: Int) {
        out.update(repeating: 0, count: frames * stride)
        lock.lock(); defer { lock.unlock() }
        let fill = Double(writeIndex) - readPosition
        if !primed {
            guard fill >= target else { return }
            primed = true
        }
        // One-pole filter over several seconds of callbacks: bursts average out and only the
        // real clock difference moves the ratio, by at most 0.5 %.
        smoothedFill += (fill - smoothedFill) * 0.002
        let correction = max(-0.005, min(0.005, (smoothedFill - target) / target * 0.01))
        let ratio = baseRatio * (1 + correction)

        for frame in 0..<frames {
            if Double(writeIndex) - readPosition < 2 {  // underrun: silence, then re-prime
                primed = false
                return
            }
            let base = Int(readPosition)
            let t = Float(readPosition - Double(base))
            let a = (base % capacity) * 2
            let b = ((base + 1) % capacity) * 2
            let left = ring[a] + (ring[b] - ring[a]) * t
            let right = ring[a + 1] + (ring[b + 1] - ring[a + 1]) * t
            if stride > 1 {
                out[frame * stride] = left
                out[frame * stride + 1] = right
            } else {
                out[frame] = (left + right) / 2
            }
            readPosition += ratio
        }
    }

    /// Frames waiting to be played.
    var fill: Double {
        lock.lock(); defer { lock.unlock() }
        return Double(writeIndex) - readPosition
    }
}
