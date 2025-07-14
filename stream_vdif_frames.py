import numpy as np
import socket
import struct
import time

# Configuration
DEST_IP = '10.8.81.20'
DEST_PORT = 50000
SAMPLE_RATE = 2e6
FRAME_DURATION = 1e-3    # VDIF frame duration: 1ms
BITS_PER_SAMPLE = 2      # 2-bit quantization
CHANNELS = 1
THREAD_ID = 0            # VDIF thread ID
STATION_ID = 'AA'        # 2-char station ID
PAYLOAD_SIZE = 8000      # VDIF payload size (in bytes per frame)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def create_vdif_header(epoch_seconds, frame_number):
    # Simple VDIF header (as per VDIF specification==32 bytes?)
    header = bytearray(32)

    # Word 0: seconds from reference epoch (30 bits), legacy mode = 0
    struct.pack_into('>I', header, 0, epoch_seconds & 0x3FFFFFFF)

    # Word 1: frame number within second, log2 channels-1, bits/sample-1, thread ID
    word1 = ((frame_number & 0xFFFFFF) << 8) | ((int(np.log2(CHANNELS)) & 0x1F) << 3) | ((BITS_PER_SAMPLE-1) & 0x07)
    struct.pack_into('>I', header, 4, word1)

    # Word 2: Station ID (ASCII), VDIF version, Data type = 0 (real data)
    word2 = (ord(STATION_ID[0]) << 24) | (ord(STATION_ID[1]) << 16) | (1 << 8)
    struct.pack_into('>I', header, 8, word2)

    # Word 3: Frame length (units of 8 bytes), complex=0, bits/sample-1
    frame_length_units = (len(header) + PAYLOAD_SIZE) // 8
    word3 = (frame_length_units & 0xFFFFFF) << 8
    struct.pack_into('>I', header, 12, word3)

    # Remaining header words (4-7) set to zero for simplicity
    return header

def quantize_signal(signal):
    # 2-bit quantization into [0,1,2,3]
    #thresholds = np.percentile(signal, [25, 50, 75])
    #quantized = np.digitize(signal, thresholds, right=True)
    #return quantized.astype(np.uint8)  # values: 0,1,2,3
    return np.clip(np.floor(signal), 0, 255).astype(np.uint8)

def generate_payload(samples):
    # Pack 2-bit samples into bytes (4 samples per byte)
    packed = bytearray()
    for i in range(0, len(samples), 4):
        byte = 0
        for bit_pos in range(4):
            if i + bit_pos < len(samples):
                val = samples[i + bit_pos] & 0x03
            else:
                val = 0
            byte |= val << (6 - 2 * bit_pos)
        packed.append(byte)
    return packed

def generate_and_send_frames(duration_seconds=2):
    samples_per_frame = int(SAMPLE_RATE * FRAME_DURATION)
    epoch_start = int(time.time())
    num_frames = int(duration_seconds / FRAME_DURATION)

    t = np.arange(samples_per_frame) / SAMPLE_RATE
    frequency = 1e6

    for frame_num in range(num_frames):
        epoch_seconds = epoch_start + int(frame_num * FRAME_DURATION)

        # Generate sine wave with noise
        signal = np.sin(2 * np.pi * frequency * t) + np.random.normal(0, 0.2, samples_per_frame)

        # Quantize
        quantized_signal = quantize_signal(signal)

        # Generate payload
        payload = generate_payload(quantized_signal)[:PAYLOAD_SIZE]

        # VDIF Header
        header = create_vdif_header(epoch_seconds, frame_num)

        # Full frame
        vdif_frame = header + payload

        # Send UDP frame
        sock.sendto(vdif_frame, (DEST_IP, DEST_PORT))

        # Sleep until next frame
        time.sleep(FRAME_DURATION)

if __name__ == "__main__":
    print(f"Sending VDIF frames to {DEST_IP}:{DEST_PORT}")
    generate_and_send_frames(duration_seconds=1)
