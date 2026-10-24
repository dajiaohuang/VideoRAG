import importlib.util
import sys
import types
from pathlib import Path
from unittest.mock import Mock


def test_empty_segment_batch_does_not_load_whisper(monkeypatch):
    package_path = Path(__file__).parents[1] / "videorag"
    videoutil_package = types.ModuleType("videorag._videoutil")
    videoutil_package.__path__ = [str(package_path / "_videoutil")]
    package = types.ModuleType("videorag")
    package.__path__ = [str(package_path)]
    monkeypatch.setitem(sys.modules, "videorag", package)
    monkeypatch.setitem(sys.modules, "videorag._videoutil", videoutil_package)

    whisper_model = Mock(return_value=types.SimpleNamespace(logger=Mock()))
    faster_whisper = types.ModuleType("faster_whisper")
    faster_whisper.WhisperModel = whisper_model
    tqdm_module = types.ModuleType("tqdm")
    tqdm_module.tqdm = lambda values, **kwargs: values
    transformers = types.ModuleType("transformers")
    transformers.AutoModelForSpeechSeq2Seq = Mock()
    transformers.AutoProcessor = Mock()
    transformers.pipeline = Mock()
    for name, module in (
        ("torch", types.ModuleType("torch")),
        ("faster_whisper", faster_whisper),
        ("tqdm", tqdm_module),
        ("transformers", transformers),
    ):
        monkeypatch.setitem(sys.modules, name, module)

    module_name = "videorag._videoutil.asr"
    module_path = package_path / "_videoutil" / "asr.py"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, module_name, module)
    spec.loader.exec_module(module)

    assert module.speech_to_text("empty", "unused", {}, "mp3") == {}
    whisper_model.assert_not_called()
