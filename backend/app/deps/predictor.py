from app.ports.predictor import HeuristicPredictor, PredictorPort

_predictor = HeuristicPredictor()


def get_predictor() -> PredictorPort:
    return _predictor
