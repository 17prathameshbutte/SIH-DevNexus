class AppState:
    def __init__(self):
        self.settings = None
        self.emitters = []
        self.pulses = []
        self.bands = []
        self.band_manager = None
        self.environment = None
        self.receiver = None
        self.engine = None
        self.current_scheduler = None
        self.scan_history = []
        self.model_loaded = False
        self.predictor = None
        self.feature_extractor = None

app_state = AppState()
