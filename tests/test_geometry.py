import numpy as np

from core.geometry import antenna_heights_msl, los_height


def test_los_is_horizontal_for_equal_endpoint_heights():
    H_tx_m, H_rx_m = antenna_heights_msl(
        z_tx_m=0.0,
        h_tx_m=10.0,
        z_rx_m=0.0,
        h_rx_m=10.0,
    )
    d1_m = np.linspace(0.0, 10_000.0, 201)
    h_los_m = los_height(H_tx_m, H_rx_m, d1_m, 10_000.0)
    assert np.allclose(h_los_m, 10.0)


def test_los_professor_example():
    H_tx_m, H_rx_m = antenna_heights_msl(
        z_tx_m=0.0,
        h_tx_m=110.0,
        z_rx_m=0.0,
        h_rx_m=150.0,
    )
    h_los_m = los_height(
        H_tx_m,
        H_rx_m,
        np.array([8_000.0]),
        20_000.0,
    )
    assert abs(h_los_m[0] - 126.0) < 0.1
