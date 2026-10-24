import importlib.util
import json
import os
import sys
import types
from pathlib import Path
from types import SimpleNamespace

import pytest


SCRIPT = (
    Path(__file__).parents[1]
    / "reproduce"
    / "quantitative_comparison"
    / "batch_quant_eval_download.py"
)


def load_downloader(monkeypatch, client_factory):
    openai = types.ModuleType("openai")
    openai.OpenAI = client_factory
    monkeypatch.setitem(sys.modules, "openai", openai)

    jsonlines = types.ModuleType("jsonlines")
    tiktoken = types.ModuleType("tiktoken")
    tqdm = types.ModuleType("tqdm")
    tqdm.tqdm = lambda values, *args, **kwargs: values
    for name, module in (
        ("jsonlines", jsonlines),
        ("tiktoken", tiktoken),
        ("tqdm", tqdm),
    ):
        monkeypatch.setitem(sys.modules, name, module)

    spec = importlib.util.spec_from_file_location("quant_downloader_under_test", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_import_has_no_api_calls_and_preserves_environment_key(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "synthetic-openai-key")
    constructions = []
    retrievals = []

    class FakeClient:
        def __init__(self):
            constructions.append(self)
            self.batches = SimpleNamespace(retrieve=self.retrieve)
            self.files = SimpleNamespace(content=self.content)

        def retrieve(self, batch_id):
            retrievals.append(batch_id)
            return SimpleNamespace(output_file_id="synthetic-output")

        def content(self, file_id):
            raise AssertionError("import must not download files")

    load_downloader(monkeypatch, FakeClient)

    assert constructions == []
    assert retrievals == []
    assert os.environ["OPENAI_API_KEY"] == "synthetic-openai-key"


def test_batch_output_id_is_retrieved_once(monkeypatch):
    module = load_downloader(monkeypatch, lambda: None)
    retrievals = []
    client = SimpleNamespace(
        batches=SimpleNamespace(
            retrieve=lambda batch_id: retrievals.append(batch_id)
            or SimpleNamespace(output_file_id="synthetic-output")
        )
    )

    module.obtain_ouput_file_id(["batch-1"], client=client)

    assert retrievals == ["batch-1"]


def test_download_decodes_utf8_and_removes_temp_file(monkeypatch, tmp_path):
    module = load_downloader(monkeypatch, lambda: None)
    monkeypatch.chdir(tmp_path)
    result_dir = tmp_path / "batch_requests" / "fixture"
    result_dir.mkdir(parents=True)
    payload = '{"custom_id":"synthetic","text":"café ☕"}\n'.encode("utf-8")
    fake_client = SimpleNamespace(
        files=SimpleNamespace(
            content=lambda file_id: SimpleNamespace(content=payload)
        )
    )

    module.download_result(["output-1"], "fixture", client=fake_client)

    result_path = result_dir / "output-1.json"
    assert json.loads(result_path.read_text(encoding="utf-8")) == [
        {"custom_id": "synthetic", "text": "café ☕"}
    ]
    assert not (result_dir / "output-1.temp").exists()


def test_download_removes_temp_after_invalid_json(monkeypatch, tmp_path):
    module = load_downloader(monkeypatch, lambda: None)
    monkeypatch.chdir(tmp_path)
    result_dir = tmp_path / "batch_requests" / "fixture"
    result_dir.mkdir(parents=True)
    fake_client = SimpleNamespace(
        files=SimpleNamespace(
            content=lambda file_id: SimpleNamespace(content=b"not-json\n")
        )
    )

    with pytest.raises(ValueError):
        module.download_result(["output-2"], "fixture", client=fake_client)

    assert not (result_dir / "output-2.temp").exists()
