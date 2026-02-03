"""
Audio processing utilities
"""
import base64
import numpy as np
import logging

logger = logging.getLogger(__name__)


def mulaw_decode(mulaw_data: bytes) -> bytes:
    """
    Decode mu-law encoded audio to PCM

    Args:
        mulaw_data: mu-law encoded audio bytes

    Returns:
        bytes: PCM audio bytes (16-bit signed integers)
    """
    try:
        # Convert bytes to numpy array
        mulaw_array = np.frombuffer(mulaw_data, dtype=np.uint8)

        # mu-law decompression lookup table
        MULAW_BIAS = 0x84
        MULAW_MAX = 0x1FFF

        # Convert mu-law to linear PCM
        mulaw_array = ~mulaw_array
        sign = (mulaw_array & 0x80)
        exponent = (mulaw_array & 0x70) >> 4
        mantissa = mulaw_array & 0x0F

        # Compute linear value
        linear = ((mantissa << 3) + MULAW_BIAS) << exponent
        linear = linear - MULAW_BIAS

        # Apply sign
        linear = np.where(sign != 0, -linear, linear)

        # Convert to int16
        pcm_array = linear.astype(np.int16)

        return pcm_array.tobytes()

    except Exception as e:
        logger.error(f"Failed to decode mu-law audio: {e}")
        raise


def mulaw_encode(pcm_data: bytes) -> bytes:
    """
    Encode PCM audio to mu-law

    Args:
        pcm_data: PCM audio bytes (16-bit signed integers)

    Returns:
        bytes: mu-law encoded audio bytes
    """
    try:
        # Convert bytes to numpy array
        pcm_array = np.frombuffer(pcm_data, dtype=np.int16)

        # mu-law compression
        MULAW_BIAS = 0x84
        MULAW_MAX = 0x1FFF

        # Get sign
        sign = (pcm_array < 0).astype(np.uint8) << 7
        linear = np.abs(pcm_array).astype(np.int32)

        # Add bias
        linear = np.clip(linear + MULAW_BIAS, 0, MULAW_MAX)

        # Find exponent
        exponent = np.zeros_like(linear, dtype=np.uint8)
        for i in range(7, -1, -1):
            mask = (linear >= (1 << (i + 3)))
            exponent = np.where(mask & (exponent == 0), i, exponent)

        # Extract mantissa
        mantissa = ((linear >> (exponent + 3)) & 0x0F).astype(np.uint8)

        # Construct mu-law byte
        mulaw = ~(sign | (exponent << 4) | mantissa)
        mulaw_array = mulaw.astype(np.uint8)

        return mulaw_array.tobytes()

    except Exception as e:
        logger.error(f"Failed to encode PCM to mu-law: {e}")
        raise


def base64_to_audio(base64_data: str, encoding: str = "mulaw") -> bytes:
    """
    Convert base64 encoded audio to raw bytes

    Args:
        base64_data: Base64 encoded audio string
        encoding: Audio encoding format ('mulaw' or 'pcm')

    Returns:
        bytes: Raw audio bytes (PCM format)
    """
    try:
        # Decode base64
        audio_bytes = base64.b64decode(base64_data)

        # Decode mu-law if needed
        if encoding == "mulaw":
            audio_bytes = mulaw_decode(audio_bytes)

        return audio_bytes

    except Exception as e:
        logger.error(f"Failed to convert base64 to audio: {e}")
        raise


def audio_to_base64(audio_bytes: bytes, encoding: str = "mulaw") -> str:
    """
    Convert raw audio bytes to base64 encoded string

    Args:
        audio_bytes: Raw audio bytes (PCM format)
        encoding: Target audio encoding ('mulaw' or 'pcm')

    Returns:
        str: Base64 encoded audio string
    """
    try:
        # Encode to mu-law if needed
        if encoding == "mulaw":
            audio_bytes = mulaw_encode(audio_bytes)

        # Encode to base64
        base64_data = base64.b64encode(audio_bytes).decode('utf-8')

        return base64_data

    except Exception as e:
        logger.error(f"Failed to convert audio to base64: {e}")
        raise


def resample_audio(audio_bytes: bytes, from_rate: int, to_rate: int) -> bytes:
    """
    Resample audio from one sample rate to another

    Args:
        audio_bytes: Raw PCM audio bytes
        from_rate: Source sample rate
        to_rate: Target sample rate

    Returns:
        bytes: Resampled PCM audio bytes
    """
    try:
        from scipy import signal

        # Convert to numpy array
        audio_array = np.frombuffer(audio_bytes, dtype=np.int16)

        # Calculate resampling ratio
        num_samples = int(len(audio_array) * to_rate / from_rate)

        # Resample
        resampled = signal.resample(audio_array, num_samples)
        resampled_array = resampled.astype(np.int16)

        return resampled_array.tobytes()

    except Exception as e:
        logger.error(f"Failed to resample audio: {e}")
        raise
