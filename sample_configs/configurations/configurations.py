configurations = {
    "ds8vm1": {
        "app_clk_freq": 125_000_000,
        "trigger_rate": 0.1,
        "rtm_name": "RTM_DS8VM1",
        "dma_length": 16384,
        "ad9510_input": 1,
        "ad9510_division": 2,
        "pll_config": "clock_distribution",
    },
    "dwc8vm1": {
        "app_clk_freq": 125_000_000,
        "trigger_rate": 0.1,
        "rtm_name": "RTM_DWC8VM1",
        "dma_length": 16384,
        "ad9510_input": 1,
        "ad9510_division": 2,
        "pll_config": "162_5MHz_to_121_875MHz_clock",
    },
    "dwc8vm1_w_rtm_clk": {
        "app_clk_freq": 125_000_000,
        "trigger_rate": 0.1,
        "rtm_name": "RTM_DWC8VM1",
        "dma_length": 16384,
        "ad9510_input": 0,
        "ad9510_division": 1,
        "pll_config": "162_5MHz_to_121_875MHz_clock",
    },
}
