"""Pytest configuration and fixtures for test suite."""

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest
import yaml

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture
def mock_config():
    """Provide mock configuration for testing."""
    return {
        "detection": {
            "confidence_threshold": 0.25,
            "nms_threshold": 0.45,
            "classes": ["norway_rat", "roof_rat"],
        },
        "model": {
            "path": "models/best.onnx",
            "input_size": [640, 640],
        },
        "alerts": {
            "cooldown_minutes": 10,
            "max_alerts_per_hour": 6,
        },
        "twilio": {
            "enabled": True,
        },
        "camera": {
            "source": "/mnt/wyze_sd",
            "fps": 30,
            "resolution": [1920, 1080],
        },
    }


@pytest.fixture
def mock_twilio_client():
    """Provide mock Twilio client."""
    client = MagicMock()
    client.messages.create.return_value = MagicMock(sid="TEST_MESSAGE_SID")
    return client


@pytest.fixture
def sample_image_path(tmp_path):
    """Create a temporary test image."""
    import numpy as np
    from PIL import Image

    # Create a dummy image
    img_array = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
    img = Image.fromarray(img_array)
    
    # Save to temp path
    img_path = tmp_path / "test_image.jpg"
    img.save(img_path)
    
    return str(img_path)


@pytest.fixture
def mock_onnx_session():
    """Mock ONNX runtime session."""
    session = MagicMock()
    
    # Mock input/output specs
    session.get_inputs.return_value = [
        MagicMock(name="images", shape=[1, 3, 640, 640])
    ]
    session.get_outputs.return_value = [
        MagicMock(name="output0", shape=[1, 25200, 7])
    ]
    
    # Mock inference
    import numpy as np
    mock_output = np.random.rand(1, 25200, 7).astype(np.float32)
    session.run.return_value = [mock_output]
    
    return session


@pytest.fixture
def detection_result():
    """Sample detection result."""
    return {
        "timestamp": "2024-09-19T10:00:00",
        "detections": [
            {
                "class": "norway_rat",
                "confidence": 0.85,
                "bbox": [100, 100, 200, 200],
            }
        ],
        "image_path": "/data/images/detection_001.jpg",
    }


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Set mock environment variables."""
    env_vars = {
        "TWILIO_ACCOUNT_SID": "AC_TEST_SID",
        "TWILIO_AUTH_TOKEN": "TEST_TOKEN",
        "TWILIO_FROM_NUMBER": "+1234567890",
        "ALERT_PHONE_NUMBER": "+0987654321",
    }
    
    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)
    
    return env_vars


@pytest.fixture(autouse=True)
def cleanup_test_files(tmp_path, request):
    """Clean up test files after each test."""
    yield
    # Cleanup logic here if needed
    pass